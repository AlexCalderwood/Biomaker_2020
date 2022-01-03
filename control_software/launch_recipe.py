from logging_utils import convert_recipe_line, create_new_dir, save_data
from serial_utils import open_serial, send_request, read_reply
from camera_utils import get_camera_port, initialise_RGB, initialise_NIR, initialise_MIR, set_picamera_gains, get_video_object
from time import sleep
from datetime import datetime
import os, sys
import cv2
import numpy as np


def run(recipe):

    read_path = "recipes/"
    start_time = None
    save_path = None
    dirname = ""
    
    # Open serial link with Arduino
    ser = None

    # Initialise all cameras
    RGBCamera = None
    NIRCamera = None
    MIRCamera = None
    EXPOSURE_SET = False
    
    RGB_RECORDING = False
    NIR_RECORDING = False
    MIR_RECORDING = False

    try:
        with open(read_path+recipe) as f:  # Open recipe file
            f.readline() # Skip first line containing headers
            for line in f:
                line = line.strip()  # Remove any newline or endline characters
                data = convert_recipe_line(line)  # Extract data from string to correct formats

                if start_time is None:  # First time opening a line
                    start_time = data[0]  # Obtain start time of logging (first entry)
                    save_path = "recorded_data/"  # Place to save the data
                    dirname = start_time.strftime("%Y-%m-%d-%H_%M_%S")  # Convert start time to string format
                    dirname = create_new_dir(save_path, dirname)  # Create new folder to put data in, and retrieve created folder name
                    os.makedirs(save_path + dirname + "/raw_data")
                    os.makedirs(save_path + dirname + "/processed_data")
                    
                    headers = "Time, T0, T1, T2, T3, T4, T5"  # Headers of logfile
                    with open(f"{save_path}{dirname}/raw_data/{dirname}.tmp", "a") as datafile:  # Create new logfile
                        datafile.write(headers + "\n")  # Write headers with a newline character on the end
                while True:
                    now = datetime.now()
                    time_to_wait = (data[0] - now).total_seconds()
                    print("Time to wait:", time_to_wait)
                    if RGB_RECORDING:
                        pass
                    if NIR_RECORDING:
                        _, NIRimg = NIRCamera.read()
                        NIRimg = cv2.rotate(NIRimg, cv2.ROTATE_180)
                        NIRimgs.append(NIRimg)
                        #NIRVideo.write(NIRimg)
                        print(datetime.now() - now)
                        print()
                    if MIR_RECORDING:
                        pass
                    if  time_to_wait <= 0:  # Time to carry out command
                        print("data:", data[1:])
                        if data[1] == 0:  # Read diagnostics
                            send_request(ser, data[1:])
                            reply = read_reply(ser)
                            print("Diagnostic data requested at", datetime.now())
                            print()
                            print("Target temperature:", reply[1]/10)
                            print("Blue intensity:", reply[2])
                            print("IR intensity:", reply[3])
                            print("White intensity:", reply[4])
                            print("Red intensity:", reply[5])
                            print("CFI active:", reply[6])
                            print("LEDs enabled:", reply[7])
                            print("Bed peltiers enabled:", reply[8])
                            print()
                        elif data[1] == 1:  # Set lights
                            send_request(ser, data[1:])  # Send request from file excluding date/time
                            reply = read_reply(ser)
                        elif data[1] == 2:  # Set target temperature
                            send_request(ser, data[1:])
                            reply = read_reply(ser)
                        elif data[1] == 3:  # Read temperatures and save to file
                            logtimestr = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                            send_request(ser, data[1:])
                            reply = read_reply(ser)
                            save_data(save_path, dirname, [logtimestr] + [x/10 for x in reply[1:-2]])
                        elif data[1] == 4:  # Set CFI procedure
                            send_request(ser, data[1:])
                            reply = read_reply(ser)
                        elif data[1] == 5:  # Trigger CFI
                            send_request(ser, data[1:])
                            reply = read_reply(ser)
                        elif data[1] == 6:  # Enable/disable LEDs
                            send_request(ser, data[1:])
                            reply = read_reply(ser)
                        elif data[1] == 7:  # Enable/disable bed peltiers
                            send_request(ser, data[1:])
                            reply = read_reply(ser)
                        elif data[1] == 8:  # Read stored CFI recipe
                            send_request(ser, data[1:])
                            reply = read_reply(ser)
                        elif data[1] == 9:  # Take RGB image
                            RGBtimestr = datetime.now().strftime("%Y-%m-%d-%H_%M_%S")
                            RGBimg = np.empty((2464, 3296, 3), dtype=np.uint8)
                            try:
                                RGBCamera.capture(RGBimg, 'bgr')
                            except Exception as e:
                                print("Picamera error:", e)
                        elif data[1] == 10:  # Take NIR image
                            NIRtimestr = datetime.now().strftime("%Y-%m-%d-%H_%M_%S")
                            _, NIRimg = NIRCamera.read()
                            NIRimg = cv2.rotate(NIRimg, cv2.ROTATE_180)
                        elif data[1] == 11:  # Take MIR image
                            MIRtimestr = datetime.now().strftime("%Y-%m-%d-%H_%M_%S")
                            MIRimg = MIRCamera.grab(MIR_PORT)
                        elif data[1] == 12:  # Save latest RGB image
                            cv2.imwrite(f"{save_path}{dirname}/raw_data/RGB{RGBtimestr}.jpg", RGBimg)
                        elif data[1] == 13:  # Save latest NIR image
                            cv2.imwrite(f"{save_path}{dirname}/raw_data/NIR{NIRtimestr}.jpg", NIRimg) 
                        elif data[1] == 14:  # Save latest MIR image
                            cv2.imwrite(f"{save_path}{dirname}/raw_data/MIR{MIRtimestr}.jpg", MIRimg)
                        elif data[1] == 15:  # Initialise RGB recording
                            pass
                        elif data[1] == 16:  # Initialise NIR recording
                            NIRVtimestr = datetime.now().strftime("%Y-%m-%d-%H_%M_%S")
                            NIRVideo = get_video_object(f"{save_path}{dirname}/raw_data/NIR{NIRVtimestr}.avi", 12.0, (1920,1080), "MJPG")
                        elif data[1] == 17:  # Initialise MIR recording
                            pass
                        elif data[1] == 18:  # Start RGB recording
                            RGB_RECORDING = True
                            RGBVtimestr = datetime.now().strftime("%Y-%m-%d-%H_%M_%S")
                            RGBCamera.start_recording(f"{save_path}{dirname}/raw_data/RGB{RGBVtimestr}.mjpeg")
                        elif data[1] == 19:  # Start NIR recording
                            NIR_RECORDING = True
                            NIRimgs = []
                        elif data[1] == 20:  # Start MIR recording
                            MIR_RECORDING = True
                        elif data[1] == 21:  # Stop RGB recording
                            RGB_RECORDING = False
                            RGBCamera.stop_recording()
                        elif data[1] == 22:  # Stop NIR recording
                            NIR_RECORDING = False
                        elif data[1] == 23:  # Stop MIR recording
                            MIR_RECORDING = False
                        elif data[1] == 24:  # Start fast RGB record
                            RGBVtimestr = datetime.now().strftime("%Y-%m-%d-%H_%M_%S")
                            RGBCamera.start_recording(f"{save_path}{dirname}/raw_data/RGB{RGBVtimestr}.mjpeg")
                            RGBCamera.wait_recording(data[2])
                            RGBCamera.stop_recording()
                        elif data[1] == 25:  # Start fast NIR record
                            start_time = datetime.now()
                            while (datetime.now() - start_time).total_seconds() < data[2]:
                                print("here1", datetime.now())
                                _, NIRimg = NIRCamera.read()
                                print("here2", datetime.now())
                                NIRimg = cv2.rotate(NIRimg, cv2.ROTATE_180)
                                print("here3", datetime.now())
                                NIRVideo.write(NIRimg)
                                print("here4", datetime.now())
                                print()
                            cv2.destroyAllWindows()
                        elif data[1] == 26:  # Start fast MIR record
                            pass
                        elif data[1] == 27:  # Enable RGBCamera
                            RGBCamera = initialise_RGB()
                        elif data[1] == 28:  # Enable NIRCamera
                            NIR_PORT = get_camera_port("USB 2.0 Camera")
                            NIRCamera = initialise_NIR(NIR_PORT)
                        elif data[1] == 29:  # Enable MIRCamera
                            MIR_PORT = get_camera_port("PureThermal")
                            MIRCamera = initialise_MIR()
                        elif data[1] == 30:  # Set RGB camera gains                            
                            # Enable LEDs
                            send_request(ser, [6, 1])
                            if read_reply(ser)[0] == None:
                                raise RuntimeError("Arduino returned erroneous instruction primary key - LEDs may not be enabled")

                            # Turn on white lights
                            send_request(ser, [1, 0, 0, 50, 0])  # Turn on white lights to calibrate camera
                            if read_reply(ser)[0] == None:  # If the PK of the response is erroneous throw and error
                                raise RuntimeError("Arduino returned erroneous instruction primary key - picamera gains may not be set")
                            EXPOSURE_SET = True
                            if True:# or set_picamera_gains(RGBCamera, ser, 1, 0.1):  # If picamera gains have been set successfully
                                EXPOSURE_SET = True
                                send_request(ser, [1, 0, 0, 0 ,0])  # Turn off calibration lights
                                read_reply(ser)                     # Read arduino response from buffer (to clear buffer)
                                sleep(0.1)
                        elif data[1] == 31:  # Enable serial
                            ser = open_serial("/dev/ttyACM0")
                        elif data[1] == 32:  # Disable RGBCamera
                            RGBCamera.close()
                        elif data[1] == 33:  # Disable NIRCamera
                            NIRCamera.release()
                        elif data[1] == 34:  # Disable MIRCamera
                            MIRCamera.close()
                        elif data[1] == 35:  # Disable serial
                            ser.close()
                        elif data[1] == 36:  # Sleep
                            sleep(data[2])
                        elif data[1] == 37:  # Save NIR video
                            for img in NIRimgs:
                                NIRVideo.write(img)
                        break  # Move onto next line of file
                    elif time_to_wait < 3 and not (RGB_RECORDING or NIR_RECORDING or MIR_RECORDING):  # Start 'high-speed' polling at t-3 seconds
                        sleep(0.1)
                    elif not (RGB_RECORDING or NIR_RECORDING or MIR_RECORDING):
                        print("Resting")
                        sleep(time_to_wait - 2.5)  # Wake up just before required time
    except Exception as e:
        with open(f"{save_path}{dirname}/raw_data/{dirname}.tmp", "a") as datafile:  # Create new logfile
            print("Log error:", e)
            datafile.write("\n\n{logtimestr}: " + str(e))  # Write headers with a newline character on the end
        if ser is not None:
            send_request(ser, [6, 0])  # Disable LEDs
    finally:
        if ser is not None:
            send_request(ser, [1, 0, 0, 0, 0])  # Set LEDs to off (for good measure)
        #os.rename(f"{save_path}{dirname}/raw_data/{dirname}.tmp", f"{save_path}{dirname}/raw_data/{dirname}.txt")       
        with open(f"{save_path}{dirname}/raw_data/{dirname}.tmp", 'r') as tmp:
            with open(f"{save_path}{dirname}/raw_data/{dirname}.txt", 'w') as txt:
                txt.write(tmp.read())
        os.remove(f"{save_path}{dirname}/raw_data/{dirname}.tmp")

        # Tidy up everything
        try:
            ser.close()
        except AttributeError:
            pass
        try:
            RGBCamera.close()
        except AttributeError:
            pass
        try:
            NIRCamera.release()
        except AttributeError:
            pass
        try:
            MIRCamera.close()
        except AttributeError:
            pass

if __name__ == "__main__":
    if len(sys.argv) > 1:
        if os.path.exists("recipes/" + sys.argv[1]):
            run(sys.argv[1])
        else:
            print("Invalid recipe name:", sys.argv[1])
    else:
        print("No recipe name provided: \"python3 launch_recipe.py <recipe_name>.csv")
