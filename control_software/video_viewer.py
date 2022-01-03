import cv2
import sys
import os

def run(video_name):
    video = cv2.VideoCapture(video_name)
    PAUSED = True
    ret, frame = video.read()
    try:
        while True:
            if not PAUSED:
                ret, frame = video.read()
            if not ret:
                break
            
            cv2.imshow("Video", frame)
            
            key = cv2.waitKey(1)
            if key == 27:  # ESC
                break
            elif key == 32:
                PAUSED = not PAUSED  # Toggle paused
            elif key == 13 and PAUSED:
                ret, frame = video.read()
    finally:
        video.release()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    if len(sys.argv) > 1:
        if os.path.exists("recorded_data/" + sys.argv[1]):
            run("recorded_data/"+str(sys.argv[1]))
        else:
            print("Invalid video name:", sys.argv[1])
    else:
        print("No video name provided: \"python3 read_video.py <recipe_name>.csv")