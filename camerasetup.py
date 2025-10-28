import cv2                                      # OpenCV library for accessing and processing video frames from the camera
import time                                     # timing operations
import threading                                # running the camera in a separate thread to avoid blocking the api requests 
from datetime import datetime
import face_recognition                 
from database import SessionLocal
from faceFunctions import load_known_encodings, compare_faces
from tables import FaceEncoding
from attendence import log_attendance

CAMERA_URL = "rtsp://admin:RBCFHK@192.168.1.198:554/h264"
camera_monitoring = False           # Boolean flag telling if the camera monitoring thread is on/off
camera_thread = None                # store the (threading.Thread) object for the camera monitoring thread
camera_capture = None               # store the OpenCV(VideoCapture) object for accessing the camera



# establish a connection to the camera using the RTSP URL
def get_camera_connection():
    global camera_capture                                           # allow the function to update it (defaut=none)
    if camera_capture is not None and camera_capture.isOpened():    # check if camera_capture is already open 
        print("Camera already connected")
        return camera_capture                                       # if yes return it
    

    max_retry = 3   # counter 
    attempt = 0     # counter 
    while attempt < max_retry:
        camera_capture = cv2.VideoCapture(CAMERA_URL)   # creat a (VideoCapture) object using the RTSP-URL ,, camera_capture.read() --> give next frames
        camera_capture.set(cv2.CAP_PROP_BUFFERSIZE, 1)  # set the camera buffer size to 1 to reduce latency/lag
        camera_capture.set(cv2.CAP_PROP_FPS, 15)        # set the FPS to 15
        print(f"buffer=1, fps=15")                      # test

        if camera_capture.isOpened():                   # if (VideoCapture) object is open 
            print("Camera connected successfully")
            return camera_capture      
        print(f"Connection failed")

        if camera_capture:                  # failed 
            camera_capture.release()        # release the (VideoCapture) object to free resources before retry again
        time.sleep(2)               # wait 2 sec 
        attempt = attempt + 1

    print("Failed to connect to the camera after 3 attempts")
    return None # start over ? continue 


# start the camera stream in a separate thread
def start_camera_monitoring():
    global camera_monitoring, camera_thread, camera_capture         # declare the global variables to update/modify them using the function 

    if camera_monitoring:                                           # check if the camera is already active ?
        return {                                                    # return dictionary reply 
            "status": "already_running",
            "message": "Camera already active"
              }
    
    camera_capture = get_camera_connection()    # if the camera isn;t already active, get connection
    if camera_capture is None:                  # still not connected 
        return {
            "status": "error",
            "message": "Failed to connect to camera"
            }
    
    camera_monitoring = True                                        # Sets the (camera_monitoring) flag to True, meaning that the stream is active
    print("Starting camera monitoring thread...")
    camera_thread = threading.Thread(target=stream_camera_frames)   # Creates a new thread that runs (stream_camera_frames) function
    camera_thread.daemon = True                                     # thread as a daemon, meaning it will terminate when the main application exits
    camera_thread.start()                                           # start the thread 
    return {
        "status": "started",
        "message": "Camera started with live face detection"
          }


# the main function for processing camera frames, detecting and comparing faces, and logging.
def stream_camera_frames():
    global camera_monitoring, camera_capture              # Declares global variables to modify/update
    print("Starting camera stream with live face detection")            # test
    db = SessionLocal()                         # creat a new db session
    try:

        known_encodings = load_known_encodings(db)                      # load_known_encodings from facefunctions.py
        print(f"Loaded {len(known_encodings)} known faces")             # test

        last_flush = time.time()                                        # record the time to track when the camera buffer was last flushed

        while camera_monitoring:                # start the loop while camera_monitoring=true

            if camera_capture is None or not camera_capture.isOpened():
                print("ERROR, camera_capture=none. trying to reconnect ...")
                # whats the problem 
                if camera_capture is not None:              # check if camera_capture exists    
                    camera_capture.release()                # relaese it
                camera_capture = get_camera_connection()    # try to reconnect

                if camera_capture is None:                  # the program doesnt have any camera object 
                    print("ERROR, reconnecting failed. Retrying in 5 seconds...")
                    time.sleep(5)                           # wait 5 seconds
                    continue                                # back to the loop
                # if successful, reset last_flush && time.time() --> current time in seconds 
                last_flush = time.time()            

            if time.time() - last_flush >= 3:               # Checks if 3 seconds have passed since the last buffer flush     
                if camera_capture:                          # Ensures (camera_capture) exists before attempting to release it
                    camera_capture.release()
                camera_capture = get_camera_connection()    # reconnect ( fresh frames )

                if camera_capture is None:                  # if the reconnection failed
                    print("ERROR, reconnecting failed. Retrying in 5 seconds ...")
                    time.sleep(5)
                    continue
                # update
                last_flush = time.time()
                print("Flushed camera buffer")  # test

            ret, frame = camera_capture.read()                      # ret is a boolean flag [true,false] , frame = frame captured ?

            if not ret or frame is None or frame.size == 0:         # check if the frame capture failed or the frame is invalid (empty or zero-sized)
                print("empty/bad frame, Retrying ...")
                time.sleep(0.01)                                     # wait , maybe more ?
                continue
                                    
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)      # convert the frame from bgr -> rgb
            face_locations = face_recognition.face_locations(rgb_frame, model="hog")        # using the default model (hog) less accurate but faster than (CNN)

            if not face_locations:      # no faces , wait and go back 
                time.sleep(0.01)         # maybe more ?
                continue

            print(f"Detected {len(face_locations)} face(s)")    # how many faces detected ,, test 
            face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)     # encode all detected faces in the frame

            for camera_encoding in face_encodings:              # iterate over the detected faces 
                matched_user_id = compare_faces(known_encodings, camera_encoding, tolerance=0.6)    # call compare_faces to match

                if not matched_user_id:         # unknown face 
                    print("Unknown person detected")
                    continue                    # skip to the next face             

                user = db.query(FaceEncoding).filter(FaceEncoding.user_id == matched_user_id).first()   # query for matched_user (check if the user has a record)
                if user and user.fingerprint_enabled == True:
                    print(f"User {matched_user_id} already logged (fingerprint_enabled=True), skipping...")
                    continue        # skip

                if log_attendance(matched_user_id):     # call log_attendance function to log attendance
                    print(f"Attendance logged for user {matched_user_id}") #test
            time.sleep(0.01) # between frame processing --> reduce cpu load

    except Exception as e:
        print(f"[ERROR] Stream error: {str(e)}")

    finally:
        if camera_capture is not None and isinstance(camera_capture, cv2.VideoCapture) and camera_capture.isOpened():   # Checks if camera_capture exists, is a VideoCapture object, and is open.
            camera_capture.release()
        camera_capture = None
        db.close()
        print("camera stopped")