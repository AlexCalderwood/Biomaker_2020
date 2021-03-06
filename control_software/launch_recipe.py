from logging_utils import *
from time import sleep
import datetime
import os


def run():
    recipe = "recipe_0.csv"
    read_path = "recipes/"
    start_time = None

    with open(read_path+recipe) as f:
        f.readline() # Skip first line containing headers
        for line in f:
            line = line.strip()  # Remove any newline or endline characters
            data = convert_recipe_line(line)  # Extract data from string to correct formats

            if start_time is None:  # First time opening a line
                start_time = data[0]  # Obtain start time of logging (first entry)
                save_path = "recorded_data/"  # Place to save the data
                dirname = start_time.strftime("%y-%m-%d-%H_%M_%S")  # Convert start time to string format
                dirname = create_new_dir(save_path, dirname)  # Create new folder to put data in, and retrieve created folder name
                
                headers = "time_logged, current_temp"  # Headers of logfile
                with open(f"{save_path}{dirname}/{dirname}.txt", "a") as datafile:  # Create new logfile
                    datafile.write(headers + "\n")  # Write headers with a newline character on the end

            while True:
                now = datetime.datetime.now()
                time_to_wait = (data[0] - now).total_seconds()
                if  time_to_wait <= 0:  # Time to gather some data

                    # Gather data
                    rgb_image = request_rgb_image()
                    ir_image = request_lepton_image()
                    env_data = request_env_data()
                    new_data = [data[0], data[2] + 0.5]  # Temporary mock data

                    # Save data
                    save_data(save_path, dirname, rgb_image, ir_image, new_data)

                    # Write data to cloud?
                    concurrent_log = False
                    if concurrent_log:
                        push_to_cloud()# Maybe do at the end/in batches/in separate thread/with different program\batchfile?
                    
                    break
                elif time_to_wait < 3:  # Start high-speed polling at t-3 seconds
                    sleep(0.1)
                else:
                    sleep(time_to_wait - 2.5)  # Wake up just before required time


if __name__ == "__main__":
    run()
