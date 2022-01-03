print("Importing modules...")
from serial_utils import *
from camera_utils import *
from logging_utils import *
from time import sleep
from datetime import datetime
import numpy as np
print("Modules imported")
print()


# SPECIFY CFI PROCEDURE HERE
CFI_procedure = [4, 0,        # NECESSARY INFORMATION, KEEP FIRST NUMBER AS 4 (second number gets overwritten later)
    0,0,0,0,1000,           # Instructions are of the form: Blue, IR, White, Red, milliseconds to stay like this
    0,0,0,100,500,
    255,0,0,0,200,
    0,0,0,0,1000,
    255,0,0,0,200,
    0,0,0,0,1000,
    255,0,0,0,200,
    0,0,0,0,1000
    ]


# Automatically fill in rest of procedure details
CFI_procedure[1] = len(CFI_procedure) - 2  # Fills in number of instructions automatically
CFI_procedure += [0]*(502-len(CFI_procedure))  # Fills in rest of instructions with zeros (not necessary, just speeds up sending signal


# SPECIFY CAMERA PROCEDURE HERE
resolution = (640, 480)  # (Width, height), max = (1960, 1080)
cam_procedure = [
    0, 750,               # Instructions are of the form: video on/off (1/0), milliseconds
    1, 1000,
    0, 700,
    1, 500,
    0, 700,
    1, 500,
    0, 700
    ]
#cam_procedure = [
#    0, 1000,               # Instructions are of the form: video on/off (1/0), milliseconds
#    1, 9200,
#    0, 1000
#    ]

# ADVANCED SETTINGS
camera_delay = 295  # milliseconds
OVERLAY_TEXT = True
exposure = 16  # For best results use multiple of 16, from 1-5000 (5000 being the brightest).
vcodec = "MJPG"
vformat = "avi"
framerate = 12.0
data_location = "recorded_data/"

data_location.strip("/")
cam_procedure = [0, camera_delay] + cam_procedure # Add a bit of waiting time on the front

# Initialising NIR camera
print("Initialising NIR camera...")
NIR_PORT = get_camera_port("USB 2.0 Camera")  # Find NIR camera port
NIRCamera = initialise_NIR(NIR_PORT, exposure_absolute=exposure, resolution=resolution)  # Connect to camera and configure settings
start_time = datetime.now().strftime("%Y-%m-%d-%H_%M_%S")
NIRVideo = get_video_object(f"{data_location}/NIR{start_time}.{vformat}", framerate, resolution, vcodec)  # Create video recording object to write frames to
print("NIR initialisation complete")
print()

# Initialise serial connection
print("Opening serial connection...")
ser = open_serial("/dev/ttyACM0")
try:
    while True:  # Send request to arduino until it replies
        send_request(ser, [0])
        if len(read_reply(ser)) > 0:  # If any reply is received
            break  # Continue with the program
    print("Serial connected")
    print()

    print("Enabling LEDs...")
    send_request(ser, [6,1])  # Enables LEDs if not already
    if read_reply(ser)[0] == 6:  # Checks command was received
        print("LEDs enabled")
    print()

    print("Sending CFI procedure...")
    send_request(ser, CFI_procedure)  # Send CFI procedure to arduino
    if read_reply(ser)[0] != 4:  # Check it received the right command
        raise RuntimeError("Arduino could not interpret CFI request PK")
    send_request(ser, [8])  # Request CFI procedure from arduino to check it
    reply = read_reply(ser)
    if reply[1:-2] != CFI_procedure[2:]:  # Compare reply (excluding PK, and last two data ints in reply)
        raise RuntimeError("Arduino has incorrectly received CFI procedure")
    print("CFI procedure received")
    print()
    inp = input("Ready to initiate CFI, do you want to continue (Y/N)?")
    if (inp == "Y" or inp == "" or inp == "y"):  # Empty input or "Y" starts the CFI. Anything else cancels it.
        print("Initiating CFI...")
        send_request(ser, [5,1])  # Send request to activate CFI light procedure
        read_reply(ser)
        print("CFI procedure initiated")
        print()

        CFI_state = 0
        start_time = datetime.now()
        next_change = cam_procedure[CFI_state*2 + 1]
        frames = 0 
        while True:
            elapsed_time = (datetime.now() - start_time).total_seconds() * 1000  # Get time since start, in milliseconds
            if elapsed_time >= next_change:  # If it is time for next state
                if CFI_state >= ((len(cam_procedure)/2)-1):  # All instructions have been completed
                    break  # End the process
                CFI_state += 1  # Move to next state
                next_change += cam_procedure[CFI_state*2 + 1]  # Add on the duration of this state to the running timer
                if cam_procedure[CFI_state*2] == 0 and cam_procedure[(CFI_state-1)*2] == 1:  # If camera has just stopped recording
                    NIRVideo.write(np.zeros(shape=(resolution[1], resolution[0], 3),dtype=np.uint8))  # Insert a black frame after the end of the recording
                    print("mean frame interval:", (cam_procedure[(CFI_state-1)*2 + 1]/1000)/frames)
                    print("mean framerate:", frames/(cam_procedure[(CFI_state-1)*2 + 1]/1000))
                    print()
                    frames = 0
            if cam_procedure[CFI_state*2]:  # If the camera needs to be recording this state
                _, NIRimg = NIRCamera.read()  # Read image from camera
                NIRimg = cv2.rotate(NIRimg, cv2.ROTATE_180)  # Rotate image so it is not upside down
                r_elapsed_time = round(elapsed_time) - camera_delay
                if OVERLAY_TEXT:
                    cv2.putText(NIRimg, text=str(r_elapsed_time), org=(10,resolution[1]-20), fontFace=cv2.FONT_HERSHEY_SIMPLEX, fontScale=0.4, color=(255,255,255), thickness=1, lineType=2)
                #cv2.imwrite(f"CFI/NIR{r_elapsed_time}.png", NIRimg)
                NIRVideo.write(NIRimg)  # Add this image onto the video
                frames += 1
                
        print("Camera procedure complete. CFI light procedure may still be in progress.")

        CFI_light_duration = sum(CFI_procedure[2:][4::5])  # Calculate expected duration of CFI light procedure
        while (datetime.now() - start_time).total_seconds()*1000 < CFI_light_duration:
            pass  # Wait for lights to be completed
        print("CFI light procedure complete.")
    else:
        print("CFI procedure cancelled.")
finally:  # This code runs last, even if errors occur between here and the 'try:' statement
    send_request(ser, [5,0])  # End the CFI light procedure
    ser.close()  # Close the serial communication
    NIRCamera.release()  # Release the camera
    NIRVideo.release()  # Release the video object
