import mediapipe as mp
import cv2
import time
import pyautogui
mp_hands = mp.solutions.hands
mp_draw = mp.solutions.drawing_utils
cap = cv2.VideoCapture(0)
cap.set(3,1280)
cap.set(4,720)

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

def isPinching(finger1, finger2, hand_landmarks):
    is_active = True
    start_time = None
    dist = distance(finger1, finger2, hand_landmarks)
    if (dist < 0.05):
        if is_active:
            if start_time is None:
                start_time = time.perf_counter()

        elapsed = time.time() - start_time
        # print(elapsed)
        # print(start_time)
        # print(time.time())
        if (elapsed> 0.5):
            return True
    else:
        start_time = None

def isTap(finger1, finger2, hand_landmarks): # need to fix
    is_active = True
    start_time = None
    dist = distance(finger1, finger2, hand_landmarks)
    if (dist<0.05):
        if is_active:
            if start_time is None:
                start_time = time.perf_counter()

        elapsed = time.time() - start_time
        # print(elapsed)
        # print(start_time)
        # print(time.time())
        if (elapsed< 0.4):
            return True
    else:
        start_time = None

def volControl(finger2, hand_landmarks):
    if isPinching("THUMB_TIP", finger2, hand_landmarks):
        if (finger2 == "INDEX_FINGER_TIP"):
            pyautogui.press('volumeup')
        elif (finger2 == "MIDDLE_FINGER_TIP"):
            pyautogui.press('volumedown')

def click(finger2, hand_landmarks):
    if isTap("THUMB_TIP", finger2, hand_landmarks) :
        print("we're tapping")
        pyautogui.click()
       
def zoom (finger2, hand_landmarks):
    dist = distance("THUMB_TIP", finger2, hand_landmarks)
    #print(dist)
    #print(finger2)

    if isPinching("THUMB_TIP", finger2, hand_landmarks) :
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
    )as hands:
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
                for hand_landmarks in results.multi_hand_landmarks:
                    mp_draw.draw_landmarks(img, hand_landmarks, mp_hands.HAND_CONNECTIONS )

                volControl("INDEX_FINGER_TIP", hand_landmarks)
                volControl("MIDDLE_FINGER_TIP", hand_landmarks)
                click("INDEX_FINGER_TIP", hand_landmarks)
                zoom("RING_FINGER_TIP",hand_landmarks)
                zoom("PINKY_FINGER_TIP",hand_landmarks)

            else:
                cv2.putText(img, "no hand yet", (20,40), cv2.FONT_HERSHEY_COMPLEX, 1, (255,255,255),1, cv2.LINE_AA )

            img = cv2.imshow("Image", img)     
            if cv2.waitKey(1) & 0xFF == 27:
                break           
    cap.release()
    cv2.destroyAllWindows()
    
if __name__ == '__main__':
    main()



        

