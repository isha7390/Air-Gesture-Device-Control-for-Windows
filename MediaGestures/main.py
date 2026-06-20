import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
import cv2
import pyautogui
from collections import namedtuple
from streamlit_webrtc import webrtc_streamer
import streamlit as st
import streamlit.components.v1 as components
import threading
import av
import os
from flask import Flask, request, jsonify
from flask_cors import CORS
import time 
import webview
base_options = python.BaseOptions(model_asset_path = 'gesture_recogniser.task')
options = vision.GestureRecognizerOptions(base_options=base_options)
mp_hands = mp.solutions.hands
mp_draw = mp.solutions.drawing_utils
cap = cv2.VideoCapture(0)
cap.set(3,1280)
cap.set(4,720)


data = None
video_running = False
app = Flask(__name__)

CORS(app, resources={r"/*": {"origins": "*"}})
@app.route('/receive-data', methods=['POST'])
@app.route('/receive-data', methods=['POST'])
def receive_data():
    global data, video_running, left, right, finger, action
    try:
        data = request.get_json(force=True)
        print("\n=== DEBUG: INCOMING DATA ===")
        print(data)
        
        # Safely parse matching list components
        left   = data.get('left', [])
        right  = data.get('right', [])
        finger = data.get('finger', [])  
        action = data.get('action', [])
        
        print(f"=== DEBUG: Current video_running state is: {video_running} ===")
        
        if not video_running:
            print("=== DEBUG: Condition met! Attempting to launch thread... ===")
            video_running = True
            
            loop_thread = threading.Thread(target=main, daemon=True)
            loop_thread.start()
            
            print("=== DEBUG: Thread started successfully! ===")
            return jsonify({"status": "success", "message": "Loop started!"}), 200
        else:
            print("=== DEBUG: video_running was already True. Skipping thread launch. ===")
            return jsonify({"status": "success", "message": "Data cached successfully!"}), 200

    except Exception as e:
        print(f"\n!!! CRITICAL ROUTE ERROR !!!\n{e}")
        import traceback
        traceback.print_exc() # Prints the exact line number where it failed
        return jsonify({"status": "error", "message": str(e)}), 500

def run_background_server():
    app.run(host='127.0.0.1', port=5000, debug=False, use_reloader=False)


@app.route('/')
def home():
    return "Flask Python Backend is Running Perfectly!"


left = []
right=[]
finger=[]
action=[]



frame_count = {
    "THUMB_TIP": {
        "INDEX_FINGER_TIP": 0,
        "MIDDLE_FINGER_TIP": 0,
        "RING_FINGER_TIP": 0,
        "PINKY_FINGER_TIP":0
    },
    "INDEX_FINGER_TIP": {
        "MIDDLE_FINGER_TIP": 0,
        "RING_FINGER_TIP": 0,
        "PINKY_FINGER_TIP":0
    },
    "MIDDLE_FINGER_TIP": {
        "RING_FINGER_TIP": 0,
        "PINKY_FINGER_TIP":0
    },
    "RING_FINGER_TIP": {
        "PINKY_FINGER_TIP":0
    }
}



TOUCH_TYPES = [
    ['THUMB_TIP', 'INDEX_FINGER_TIP'],
    ['THUMB_TIP', 'MIDDLE_FINGER_TIP'],
    ['THUMB_TIP', 'RING_FINGER_TIP'],
    ['THUMB_TIP', 'PINKY_FINGER_TIP'],
    ['INDEX_FINGER_TIP', 'MIDDLE_FINGER_TIP'],
    ['INDEX_FINGER_TIP', 'RING_FINGER_TIP'],
    ['INDEX_FINGER_TIP', 'PINKY_FINGER_TIP'],
    ['MIDDLE_FINGER_TIP', 'RING_FINGER_TIP'],
    ['MIDDLE_FINGER_TIP', 'PINKY_FINGER_TIP'],
    ['RING_FINGER_TIP', 'PINKY_FINGER_TIP'],
]


FIST_DIST = [
    ['INDEX_FINGER_TIP', 'INDEX_FINGER_MCP' ],
    ['MIDDLE_FINGER_TIP', 'MIDDLE_FINGER_MCP' ],
    ['RING_FINGER_TIP', 'RING_FINGER_MCP' ],
    ['PINKY_FINGER_TIP', 'PINKY_FINGER_MCP' ]
]

fist_distances =[100,100,100,100]

finger_map = {
        "WRIST": mp_hands.HandLandmark.WRIST,
        "THUMB_CMC": mp_hands.HandLandmark.THUMB_CMC,
        "THUMB_MCP": mp_hands.HandLandmark.THUMB_MCP,
        "THUMB_IP": mp_hands.HandLandmark.THUMB_IP,
        "THUMB_TIP": mp_hands.HandLandmark.THUMB_TIP,
        "INDEX_FINGER_MCP": mp_hands.HandLandmark.INDEX_FINGER_MCP,
        "INDEX_FINGER_PIP": mp_hands.HandLandmark.INDEX_FINGER_PIP,
        "INDEX_FINGER_DIP": mp_hands.HandLandmark.INDEX_FINGER_DIP,
        "INDEX_FINGER_TIP": mp_hands.HandLandmark.INDEX_FINGER_TIP,
        "MIDDLE_FINGER_MCP": mp_hands.HandLandmark.MIDDLE_FINGER_MCP,
        "MIDDLE_FINGER_PIP": mp_hands.HandLandmark.MIDDLE_FINGER_PIP ,
        "MIDDLE_FINGER_DIP": mp_hands.HandLandmark.MIDDLE_FINGER_DIP,
        "MIDDLE_FINGER_TIP": mp_hands.HandLandmark.MIDDLE_FINGER_TIP,
        "RING_FINGER_MCP": mp_hands.HandLandmark.RING_FINGER_MCP,
        "RING_FINGER_PIP": mp_hands.HandLandmark.RING_FINGER_PIP,
        "RING_FINGER_DIP": mp_hands.HandLandmark.RING_FINGER_DIP,
        "RING_FINGER_TIP": mp_hands.HandLandmark.RING_FINGER_TIP,
        "PINKY_FINGER_MCP": mp_hands.HandLandmark.PINKY_MCP,
        "PINKY_FINGER_PIP": mp_hands.HandLandmark.PINKY_PIP,
        "PINKY_FINGER_DIP": mp_hands.HandLandmark.PINKY_DIP,
        "PINKY_FINGER_TIP": mp_hands.HandLandmark.PINKY_TIP
    }

def distance(finger1, finger2, hand_landmarks):
    
    finger1_id = finger_map[finger1]
    finger1_y = hand_landmarks.landmark[finger1_id].y
    finger1_x = hand_landmarks.landmark[finger1_id].x    
    f1x = finger1_x
    f1y = finger1_y

    finger2_id = finger_map[finger2]
    finger2_y = hand_landmarks.landmark[finger2_id].y
    finger2_x = hand_landmarks.landmark[finger2_id].x
    f2x = finger2_x
    f2y = finger2_y

    dist = ((f1x-f2x)**2 + (f1y-f2y)**2)**(0.5)
    return dist

def get_frame(finger1, finger2):
    return frame_count[finger1][finger2]

def isPinching(finger1, finger2):
    frame = get_frame(finger1, finger2)
    if frame> 4:
        print("it is pinchingnngnosndfnsofjdsfj")
        return True
    else:
        return False  

def isTap(finger1, finger2):
    frame = get_frame(finger1, finger2)
    print(frame)
    if 0<frame<5:
        # print("chekcing if this is a tap")
        # print("this is a tap")
        return True
    else:
        return False  
    
def isFist():
    fist =True
    for i in fist_distances:
        if (i>0.2):
            fist =False
    print (f"is fist is {fist}")
    return fist


def volIncrease():
    pyautogui.press('volumeup')

def volDecrease():
    pyautogui.press('volumedown')


def click():
    pyautogui.click()

def zoomIn():
    pyautogui.keyDown('ctrl')
    pyautogui.keyDown('+')
    pyautogui.keyUp('ctrl')
    pyautogui.keyUp('+')

def zoomOut():
    pyautogui.keyDown('ctrl')
    pyautogui.keyDown('-')
    pyautogui.keyUp('ctrl')
    pyautogui.keyUp('-')


def switchWin():  
    pyautogui.keyDown('alt')
    pyautogui.keyDown('tab')
    time.sleep(0.5)
    pyautogui.keyUp('alt')
    pyautogui.keyUp('tab')

gesture_dictionary = {}
action_map = {
    'vol-up': volIncrease,
    'vol-down':volDecrease,
    'zoom-in': zoomIn,
    'zoom-out': zoomOut,
    'next-window':switchWin,
    'click':click
}

def noteGest(left, right,finger,  action):
    key = tuple(left, right, finger)
    gesture_dictionary[key] =action
    print(f"mapped {key} to {action}")

def doAction():
    for l, r, f, action_name in zip(left, right, finger, action):
        left_hand_active = False
        right_hand_active = False
        finger_active = False
        # if f.lower() == 'index':
        #     f = "INDEX_FINGER_TIP"
        # elif f.lower() == 'middle':
        #     f = "MIDDLE_FINGER_TIP"
        # elif f.lower() == 'ring':
        #     f = "RING_FINGER_TIP"
        # elif f.lower() == 'pinky':
        #     f = "PINKY_FINGER_TIP"
        # elif f.lower() == 'thumb':
        #     f = "THUMB_TIP"
        
        # fist = (l == "Fist")
        # pinch = (r == "Pinch")
        # tap = (r == "Tap")
        l_clean = str(l).strip().lower()
        r_clean = str(r).strip().lower()
        f_clean = str(f).strip().lower()

        
        if f_clean == 'index':    target_finger = "INDEX_FINGER_TIP"
        elif f_clean == 'middle': target_finger = "MIDDLE_FINGER_TIP"
        elif f_clean == 'ring':   target_finger = "RING_FINGER_TIP"
        elif f_clean == 'pinky':  target_finger = "PINKY_FINGER_TIP"
        elif f_clean == 'thumb':  target_finger = "THUMB_TIP"
        else:                     target_finger = f_clean # Fallback

        left_hand_active = False
        right_hand_active = False
        finger_active = False
        
        fist  = (l_clean == "fist")
        pinch = (r_clean == "pinch")
        tap   = (r_clean == "tap")

        if fist:
            
            if isFist():
                left_hand_active = True
        else:
            
            left_hand_active = True
                

        if(pinch):
            if isPinching("THUMB_TIP", target_finger):
                right_hand_active =True
                finger_active = True
                print("is pinching")
        elif(tap):
            if isTap("THUMB_TIP", target_finger):
                right_hand_active =True
                finger_active = True
                print("is tapping")
        
        
        if left_hand_active and right_hand_active and finger_active:
            if action_name in action_map:
                print(f"it should {action_name}")
                action_map[action_name]()
                return





#--------------------------------------------------------- 


def main():
    print("this is the left hand data ------------------------")
    print(data.get('left')[0])

    with mp_hands.Hands(
        max_num_hands = 2,
        min_detection_confidence = 0.9,
        min_tracking_confidence =0.9
    ) as hands:
        while True:
            attempt =0
            success, img = cap.read()
            while not success and attempt<5:
                #time.sleep(0.2)
                success, img = cap.read()
                attempt+=1
            if not success:
                print("fail")
                break
            
            img = cv2.flip(img, 1)
            h,w,_ = img.shape
            rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB )
            results = hands.process(rgb)
            if results.multi_hand_landmarks:
                # print(results.multi_handedness)
                
                for hand_landmarks in results.multi_hand_landmarks:
                    mp_draw.draw_landmarks(img, hand_landmarks, mp_hands.HAND_CONNECTIONS )
                    
                rightIndex = -1
                leftIndex = -1
                for i in range(len(results.multi_handedness)):
                    if(results.multi_handedness[i].classification[0].label == "Right"):
                        rightIndex =i
                    elif(results.multi_handedness[i].classification[0].label == "Left"):
                        leftIndex =i
                if(len(results.multi_handedness)) ==1  and results.multi_handedness[i].classification[0].label == "Right":
                    fist_distances[0] =100

                if (rightIndex != -1):        
                    for i,j in TOUCH_TYPES:
                        dist = distance(i, j, results.multi_hand_landmarks[rightIndex])
                        if dist<0.05:
                            frame_count[i][j]+=1
                        else:
                            frame_count[i][j]=0
                    
                
                if(leftIndex != -1):
                    for a in range(len(FIST_DIST)):
                        dist = distance(FIST_DIST[a][0], FIST_DIST[a][1], results.multi_hand_landmarks[leftIndex])
                        fist_distances[a] = dist
                    
                doAction()



            else:
                cv2.putText(img, "no hand yet", (20,40), cv2.FONT_HERSHEY_COMPLEX, 1, (255,255,255),1, cv2.LINE_AA )

            img = cv2.imshow("Image", img)     
            if cv2.waitKey(1) & 0xFF == 27:
                break           
    cap.release()
    cv2.destroyAllWindows()
    
def run_flask():
    app.run(host='127.0.0.1', port=5000, debug=False, use_reloader=False)

if __name__ == '__main__':
    print("1. Starting background Flask thread...")
    flask_thread = threading.Thread(target=run_flask, daemon=True)
    flask_thread.start()
    
    print("2. Pausing briefly for server startup...")
    time.sleep(1)
    
    print("3. Attempting to open PyWebView window now...")
    # Using os.path ensures it finds index.html right next to main.py
    html_path = os.path.join(os.path.dirname(__file__), 'index.html')
    # 3. Create a local application window that loads your UI file directly
    # Replace 'index.html' with the actual path to your HTML file if it is in a different folder
    webview.create_window(
        title="Gesture Control Dashboard", 
        url="index.html", 
        width=1500, 
        height=800
    )
    
    # 4. Boot up the GUI loop (this blocks the script from exiting)
    webview.start()



