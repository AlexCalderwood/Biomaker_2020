from logging_utils import convert_recipe_line, create_new_dir, save_data, request_env_data
from serial_utils import open_serial
from image_capture.lepton_utils import LeptonCamera, LeptonError
from picamera import PiCamera
from time import sleep
from datetime import datetime
import os


def run():

    recipe = "recipe_0.csv"
    read_path = "recipes/"
    start_time = None
    picam = None
    lepcam = LeptonCamera("image_capture/raw_imgs/", "recorded_data/")
    ser = open_serial("/dev/ttyACM0")
    ser_opened = datetime.now()
    try:
        with open(read_path+recipe) as f:  # Open recipe file
            f.readline() # Skip first line containing headers
            for line in f:
                line = line.strip()  # Remove any newline or endline characters
                data = convert_recipe_line(line)  # Extract data from string to correct formats

                if start_time is None:  # First time opening a line
                    start_time = data[0]  # Obtain start time of logging (first entry)
                    save_path = "recorded_data/"  # Place to save the data
                    dirname = start_time.strftime("%y-%m-%d-%H_%M_%S")  # Convert start time to string format
                    dirname = create_new_dir(save_path, dirname)  # Create new folder to put data in, and retrieve created folder name
                    lepcam.set_img_dir(save_path+dirname)
                    
                    headers = "time_logged, t_1, t_2, h_1, h_2, light"  # Headers of logfile
                    with open(f"{save_path}{dirname}/{dirname}.txt", "a") as datafile:  # Create new logfile
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
                        env_data = request_env_data(ser, data)
                        if data[1]:
                            sleep(0.5)  # Let the white lights turn on
                            logtime = datetime.now().strftime("%y-%m-%d-%H_%M_%S")
                            print("IR Image")
                            try:
                                ir_image = lepcam.generate_img(img_name=f"IR{logtime}.png")
                            except LeptonError:
                                print("Lepton error")
                            if not picam:
                                print("Delayed PiCamera created")
                                picam = PiCamera(resolution=(3280,2464))
                                picam.rotation = 90
                                sleep(2)
                            print("RGB Image")
                            try:
                                rgb_image = picam.capture(f"{save_path}{dirname}/RBG{logtime}.jpg")
                            except Exception as e:
                                print("Picamera error:", e)
                            print("Close camera")
                            picam.close()
                            picam = None
                            # Save data
                            print("Save data")
                            save_data(save_path, dirname, env_data)

                        # Write data to cloud?
                        concurrent_log = False
                        if concurrent_log:
                            push_to_cloud()# Maybe do at the end/in batches/in separate thread/with different program\batchfile?
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
        with open(f"{save_path}{dirname}/{dirname}.txt", "a") as datafile:  # Create new logfile
            print("Log error:", e)
            datafile.write("\n\n" + str(e))  # Write headers with a newline character on the end
    finally:
        # Tidy up everything
        if picam:
            picam.close()
        ser.close()
        lepcam.clear_raw_dir()
        

if __name__ == "__main__":
    run()
