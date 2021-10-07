from logging_utils import convert_recipe_line, create_new_dir, save_data, request_env_data, read_env_data
from serial_utils import open_serial
from picamera import PiCamera
from time import sleep
from datetime import datetime
import os, sys
import cv2

def run(recipe):

    #recipe = "recipe_1.csv"
    read_path = "recipes/"
    start_time = None
    save_path = None
    dirname = ""
    picam = None
    #ser = open_serial("/dev/ttyACM0")
    ser = open_serial("COM9", timeout=5)
    ser_opened = datetime.now()
    NIRCamera = cv2.VideoCapture(0)
    #NIRCamera.set(cv2.CAP_PROP_EXPOSURE, 100)
    MIRCamera = cv2.VideoCapture(2)
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
                    
                    headers = "time_logged, t_1, t_2, h_1, h_2, light"  # Headers of logfile
                    with open(f"{save_path}{dirname}/raw_data/{dirname}.tmp", "a") as datafile:  # Create new logfile
                        datafile.write(headers + "\n")  # Write headers with a newline character on the end

                while True:
                    now = datetime.now()
                    time_to_wait = (data[0] - now).total_seconds()
                    print("Time to wait:", time_to_wait)
                    if  time_to_wait <= 0:  # Time to gather some data
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
                                sleep(2)
                            print("RGB Image")
                            try:
                                rgb_image = picam.capture(f"{save_path}{dirname}/raw_data/RBG{logtimestr}.jpg")
                                pass
                            except Exception as e:
                                print("Picamera error:", e)
                            ret, frame = NIRCamera.read()
                            cv2.imwrite(f"{save_path}{dirname}/raw_data/NIR{logtimestr}.jpg")
                            ret, frame = MIRCamera.read()
                            cv2.imwrite(f"{save_path}{dirname}/raw_data/MIR{logtimestr}.jpg")
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
                            picam = PiCamera(resolution=(3280,2464))
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
