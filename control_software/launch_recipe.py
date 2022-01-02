from logging_utils import convert_recipe_line, create_new_dir, save_data
from serial_utils import open_serial, send_request, read_reply
from camera_utils import get_camera_port, initialise_RGB, initialise_NIR, initialise_MIR, set_picamera_gains
from picamera import PiCamera
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
    ser = open_serial("/dev/ttyACM0")
    ser_opened = datetime.now()  # Record time at which serial was opened (needs time to finish)

    # Initialise all cameras
    NIR_PORT = get_camera_port("USB 2.0 Camera")
    MIR_PORT = get_camera_port("PureThermal")
    NIRCamera = initialise_NIR(NIR_PORT)
    MIRCamera = initialise_MIR()
    RGBCamera = initialise_RGB()
    EXPOSURE_SET = False

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
                    if not EXPOSURE_SET:  # Set exposure of RGB camera
                        # Check serial is functioning
                        time_since_ser = (datetime.now() - ser_opened).seconds  # Record time since ser was opened
                        if time_since_ser < 2.5:
                            sleep(2.5 - time_since_ser)   # Sleep until at least 2.5 seconds have elapsed since ser was opened
                        
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

                    else:  # Test can proceed
                        now = datetime.now()
                        time_to_wait = (data[0] - now).total_seconds()
                        print("Time to wait:", time_to_wait)
                        if  time_to_wait <= 0:  # Time to carry out command
                            print("data:", data[1:])
                            if (datetime.now() - ser_opened).total_seconds() < 2:
                                print("Preparing serial")
                                sleep(2-(datetime.now()-ser_opened).total_seconds)
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
                                cv2.imwrite(f"{save_path}{dirname}/raw_data/RBG{RGBtimestr}.jpg", RGBimg)
                            elif data[1] == 13:  # Save latest NIR image
                                cv2.imwrite(f"{save_path}{dirname}/raw_data/NIR{NIRtimestr}.jpg", NIRimg) 
                            elif data[1] == 14:  # Save latest MIR image
                                cv2.imwrite(f"{save_path}{dirname}/raw_data/MIR{MIRtimestr}.jpg", MIRimg)
                            elif data[1] == 15:  # Take RGB video
                                pass
                            elif data[1] == 16:  # Take NIR video
                                pass
                            elif data[1] == 17:  # Take MIR video
                                pass
                            break  # Move onto next line of file
                        elif time_to_wait < 3:  # Start 'high-speed' polling at t-3 seconds
                            sleep(0.1)
                        else:
                            print("Resting")
                            sleep(time_to_wait - 2.5)  # Wake up just before required time
    except Exception as e:
        with open(f"{save_path}{dirname}/raw_data/{dirname}.tmp", "a") as datafile:  # Create new logfile
            print("Log error:", e)
            datafile.write("\n\n{logtimestr}: " + str(e))  # Write headers with a newline character on the end
        send_request(ser, [6, 0])  # Disable LEDs
    finally:
        send_request(ser, [1, 0, 0, 0, 0])  # Set LEDs to off (for good measure)
        #os.rename(f"{save_path}{dirname}/raw_data/{dirname}.tmp", f"{save_path}{dirname}/raw_data/{dirname}.txt")       
        with open(f"{save_path}{dirname}/raw_data/{dirname}.tmp", 'r') as tmp:
            with open(f"{save_path}{dirname}/raw_data/{dirname}.txt", 'w') as txt:
                txt.write(tmp.read())
        os.remove(f"{save_path}{dirname}/raw_data/{dirname}.tmp")

        # Tidy up everything
        ser.close()
        RGBCamera.close()
        NIRCamera.release()
        MIRCamera.release()



def old_run(recipe):

    #recipe = "recipe_1.csv"
    read_path = "recipes/"
    start_time = None
    save_path = None
    dirname = ""
    picam = None
    ser = open_serial("/dev/ttyACM0")
    #ser = open_serial("COM9", timeout=5)
    ser_opened = datetime.now()
    NIR_PORT = get_camera_port("USB 2.0 Camera")
    MIR_PORT = get_camera_port("PureThermal")
    NIRCamera = initialise_NIR(NIR_PORT)
    MIRCamera = initialise_MIR(MIR_PORT)
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
                    if  time_to_wait <= 0:  # Time to carry out command
                        print("Env data")
                        if (datetime.now() - ser_opened).total_seconds() < 2:
                            print("Preparing serial")
                            sleep(2-(datetime.now()-ser_opened).total_seconds())
                        request_env_data(ser, data)
                        env_data = read_env_data(ser)
                        print(env_data)
                        if data[1]:
                            print("data1", data[1])
                            sleep(0.5)  # Let the white lights turn on
                            logtime = datetime.now()
                            logtimestr = logtime.strftime("%Y-%m-%d-%H_%M_%S")
                            if not picam:
                                print("Delayed PiCamera created")
                                picam = PiCamera(resolution=(3280,2464))
                                picam.rotation = 90
                                picam.exposure_compensation = -25
                                sleep(2)
                            print("RGB Image")
                            try:
                                rgb_image = picam.capture(f"{save_path}{dirname}/raw_data/RBG{logtimestr}.jpg")
                                pass
                            except Exception as e:
                                print("Picamera error:", e)
                            ret, frame = NIRCamera.read()
                            cv2.imwrite(f"{save_path}{dirname}/raw_data/NIR{logtimestr}.jpg", frame)
                            ret, frame = MIRCamera.read()
                            cv2.imwrite(f"{save_path}{dirname}/raw_data/MIR{logtimestr}.jpg", frame)
                            print("Close camera")
                            picam.close()
                            picam = None
                            # Save data
                            print("Save data")
                            env_data.insert(0, logtime)
                            save_data(save_path, dirname, env_data)
                        print("Finished")
                        print("\n\n\n")
                        break  # Move to the next line
                    elif time_to_wait < 3:  # Start high-speed polling at t-3 seconds
                        print("Polling")
                        if (not picam) and data[1]: # If the picam has not already been woken up and it needs to be
                            print("PiCamera created")
                            picam = initialise_RGB()
                            picam.rotation = 90
                        sleep(0.1)
                    else:
                        print("Resting")
                        sleep(time_to_wait - 2.5)  # Wake up just before required time
    except Exception as e:
        with open(f"{save_path}{dirname}/raw_data/{dirname}.tmp", "a") as datafile:  # Create new logfile
            print("Log error:", e)
            datafile.write("\n\n{logtimestr}: " + str(e))  # Write headers with a newline character on the end
    finally:
        #os.rename(f"{save_path}{dirname}/raw_data/{dirname}.tmp", f"{save_path}{dirname}/raw_data/{dirname}.txt")       
        with open(f"{save_path}{dirname}/raw_data/{dirname}.tmp", 'r') as tmp:
            with open(f"{save_path}{dirname}/raw_data/{dirname}.txt", 'w') as txt:
                txt.write(tmp.read())
        os.remove(f"{save_path}{dirname}/raw_data/{dirname}.tmp")

        # Tidy up everything
        if picam:
            picam.close()
            pass
        ser.close()
        NIRCamera.release()
        MIRCamera.release()
    

if __name__ == "__main__":
    if len(sys.argv) > 1:
        if os.path.exists("recipes/" + sys.argv[1]):
            run(sys.argv[1])
        else:
            print("Invalid recipe name:", sys.argv[1])
    else:
        print("No recipe name provided: \"python3 launch_recipe.py <recipe_name>.csv")
