import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
import cv2
import pyautogui
from collections import namedtuple
base_options = python.BaseOptions(model_asset_path = 'gesture_recogniser.task')
options = vision.GestureRecognizerOptions(base_options=base_options)
mp_hands = mp.solutions.hands
mp_draw = mp.solutions.drawing_utils
cap = cv2.VideoCapture(0)
cap.set(3,1280)
cap.set(4,720)


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

def volControl(finger2):  
    not_solo = isTap("THUMB_TIP", finger2)
    if (isPinching("THUMB_TIP", finger2) and not not_solo):
        if (finger2 == "INDEX_FINGER_TIP"):
            pyautogui.press('volumeup')
        elif (finger2 == "MIDDLE_FINGER_TIP"):
            pyautogui.press('volumedown')

def click(finger2):
    not_solo = isPinching("THUMB_TIP", finger2)
    if (isTap("THUMB_TIP", finger2) and not(not_solo)) :
        #print("we're tapping")
        pyautogui.click()
       
def zoom (finger2):
    if isTap("THUMB_TIP", finger2) :
        #print("thumb and "+finger2+" are tapping")
        if finger2 == "RING_FINGER_TIP":
            #print("this should zoom in")
            pyautogui.keyDown('ctrl')
            pyautogui.keyDown('+')
            pyautogui.keyUp('ctrl')
            pyautogui.keyUp('+')
        elif finger2 =="PINKY_FINGER_TIP":
            #print("this should zoom out")
            pyautogui.keyDown('ctrl')
            pyautogui.keyDown('-')
            pyautogui.keyUp('ctrl')
            pyautogui.keyUp('-')

def main():
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
                for i in range(len(results.multi_handedness)):
                    if(results.multi_handedness[i].classification[0].label == "Right"):
                        rightIndex =i
                        break

                if (rightIndex != -1):        
                    for i,j in TOUCH_TYPES:
                        dist = distance(i, j, results.multi_hand_landmarks[rightIndex])
                        if dist<0.05:
                            frame_count[i][j]+=1
                        else:
                            frame_count[i][j]=0

                    volControl("INDEX_FINGER_TIP")
                    volControl("MIDDLE_FINGER_TIP")
                    click("INDEX_FINGER_TIP")
                    zoom("RING_FINGER_TIP")
                    zoom("PINKY_FINGER_TIP")
            else:
                cv2.putText(img, "no hand yet", (20,40), cv2.FONT_HERSHEY_COMPLEX, 1, (255,255,255),1, cv2.LINE_AA )

            img = cv2.imshow("Image", img)     
            if cv2.waitKey(1) & 0xFF == 27:
                break           
    cap.release()
    cv2.destroyAllWindows()
    
if __name__ == '__main__':
    main()



        



















