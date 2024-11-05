import cv2
from ultralytics import YOLO

def shot_counter():
    yolo_model = YOLO("model_small.pt") #custom trained yolo model

    video_name = "more_shots_912.mp4"
    cap = cv2.VideoCapture(video_name)
    
    if not cap.isOpened(): #if it cant open the video file
        return "There was an error opening the file"

    #variables that track number of shots attempted and number of shots made
    shot_count = 0
    make_count = 0  

    #variables that stops objects being counted multiple times, e.g. if a make is detected, if it is detected again before a number of frames have passed, it wont count as a new make

    shot_cooldown = 0 #frames until a new shot can be counted again, starts at 0
    make_cooldown = 0 #frames until a new make can be counted again, starts at 0

    #variables used to store whether a shot or make is currently being counted 
    shot = False
    make = False

    #tracks the number of frames a shot is detected in a row
    shot_frames = 0
    #not done for 'makes' due to it appearing for a low number of frames and false detections are less common/unlikely, especially compared to the 'shots' class
    #this is because, the makes happen way faster in the video, and the dataset had much more images to train with with the class "shots" compared to "makes"

    while(cap.isOpened()):
        read, frame = cap.read() #read is assigned whether the frame has been read or not, frame is assigned the frame itself
        if not read: # wasnt able to read a new frame, meaning the video is finished
            break

        run_model = yolo_model(frame) #runs the model on each frame
        
        frame_detections = run_model[0].boxes #gets the list of boxes that are currently detected in the frame, basically gets the classes that are detected in the current frame

        #variables that track whether a shot or make has been detected or not
        shot_detected = False
        make_detected = False6

        for detection in frame_detections:
            detection_ID = detection.cls #gets the ID of the detected object
            detection_conf = detection.conf #gets the confidence score of the detected object

            if detection_ID == 0 and detection_conf > 0.8: #class_ID 0 is the class 'shot', confidence of 0.8 is used due to the model being accurate at detecting shots
                shot_detected = True #means that a shot has been detected in this curent frame

            if detection_ID == 1 and detection_conf > 0.4: #class_ID 1 is the class 'make ', confidence of 0.4 is used due to the model being  less accurate at detecting makes and false detections being less common
                make_detected = True #means that a make is detected in this current frame

        if shot_detected: 
            shot_frames += 1  #number of frames that 'shot' has been detected
            if shot_frames >= 5: #checks if shot has been detected in five frames in a row
                if not shot: #if shot is False
                    shot = True
                    shot_count +=1
                shot_cooldown = 30 #30 frames till a shot can be counted again
        else: # if a shot wasnt detected
            if shot_cooldown > 0:
                shot_cooldown -=1 #increments the shot_cooldown by one each frame
            else:
                shot = False #if shot cooldown is 0, and no shot is detected, shot equals False so no shot is in progress
            if shot_frames > 0: 
                shot_frames -= 1 # if a shot was detected one frame and then not detected in the next, it resets it zero in order to stop false detections, or random detections could add up
        
        if make_detected:
            if not make: #if make is False
                make = True
                make_count += 1
            make_cooldown = 30 #30 frames till a make can be counted again
        else: #if a make wasnt detected
            if make_cooldown > 0:
                make_cooldown -= 1 #increments the shot_cooldown by one each frame
            else:
                make = False #if make cooldown is 0, and no make is detected, make equals False so no shot is in progress
        
        if shot_count > 0: #to stop it from dividing with 0
            FG = make_count/shot_count*100
        else:
            FG = 0 
        
        #if make_count > shot_count:
        #    return "Sorry there was an error"
        
        #these three lines are only to see how it works, probably wont be needed in actual program
        cv2.putText(frame, f'Shots: {shot_count}', (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 0, 0), 2) 
        cv2.putText(frame, f'Made: {make_count}', (10, 100), cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 0, 0), 2)
        cv2.putText(frame, f'FG%: {round(FG)}%', (10, 150), cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 0, 0), 2)
        cv2.imshow('Shot Tracker', frame) #to show video, using it to see how it works

        # (10,50) = the coordinates of the text, cv3.FONT_HERSHEY_SIMPLEX = font, 2 = size of text, (0,0,0) = colour of text, 3 =  thickness of text

        if cv2.waitKey(1) & 0xFF == ord('q'): 
            break

    if shot_count > 0:
        FG = make_count/shot_count*100
    else:
        FG = 0   

    print(f"Total Number of Shots attempted: {shot_count}")
    print(f"Total Number of Shots make: {make_count}")
    print(f"Your Field Goal Percentage is: {round(FG)}%")

    cap.release()
    cv2.destroyAllWindows()

    return shot_count, make_count, FG

# if shot_count > 0:
#     FG = make_count/shot_count*100
#     print(f"Total Number of Shots attempted: {shot_count}")
#     print(f"Total Number of Shots make: {make_count}")
#     print(f"Your Field Goal Percentage is: {round(FG)}%")
# else:
#     field_goal_percentage = 0
#     print("No Shots were detected")

shot_counter()



