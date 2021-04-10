import cv2
import time
import pyautogui as pg
import copy
import mediapipe as mp

def mylog(x):
    return x**4
class Holding:
    def __init__(self):
        self.hold_status = False
        self.start = None
    def hold(self):
        # if not self.hold_status:
        self.start = time.time()
        self.hold_status = True
    def unhold(self):
        if self.hold_status:
            if time.time() - self.start > 1:
                self.hold_status = False
class Clicking:
    def __init__(self):
        self.hold = False
        self.sequence = []
        self.last_time = time.time()
        self.last_time_r = time.time()
    def right_click(self):
        if time.time() - self.last_time_r > 1:
            pg.click(button='right')
            print('right click')
            self.last_time_r = time.time()
    def click(self):
        # case-none
        if self.sequence == []:
            self.sequence.append('hold')
        elif time.time() - self.last_time < 0.8 and self.sequence == ['hold', 'unhold']:
            pg.click(button='left',clicks=2)
            print('doubleClick')
            self.sequence = ['hold']
        else:
            self.sequence = ['hold']
            
        if not self.hold:
            self.hold = True
            self.last_time = time.time()
            pg.click(button='left')
    
    def unhold(self):
        if time.time() - self.last_time < 0.8 and 'hold' in self.sequence:
            self.sequence.append('unhold')
        else:
            self.sequence = []
        self.hold = False
        
class Controller:
    def __init__(self, screen_size, camera_size):
        self.screen_size = screen_size
        self.camera_size = camera_size
        self.offset = 5
        self.clicking = Clicking()
    def update(self, frame, hand_landmark):
        index_center = hand_landmark.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP]
        thumb_center = hand_landmark.landmark[mp_hands.HandLandmark.THUMB_TIP]
        pinky_mcp_center = hand_landmark.landmark[mp_hands.HandLandmark.PINKY_MCP]
        middle_finger_mcp_center = hand_landmark.landmark[mp_hands.HandLandmark.MIDDLE_FINGER_MCP]
        middle_finger_tip_center = hand_landmark.landmark[mp_hands.HandLandmark.MIDDLE_FINGER_TIP]
        ring_finger_tip_center = hand_landmark.landmark[mp_hands.HandLandmark.RING_FINGER_TIP]
        
        is_right_hand = True if pinky_mcp_center.x > thumb_center.x else False
        if is_right_hand:
            frame = self.update_right_hand(frame, index_center)
            frame = cv2.putText(frame, str(is_right_hand), (10,30), cv2.FONT_HERSHEY_COMPLEX, 1, (255,0,0), 4)
        else:
            frame = self.update_left_hand(frame, middle_finger_mcp_center, middle_finger_tip_center, ring_finger_tip_center)
        
        return frame
    def update_left_hand(self, frame, middle_finger_mcp_center, middle_finger_tip_center, ring_finger_tip_center):
        
        if middle_finger_tip_center.y < middle_finger_mcp_center.y:
            self.clicking.click()
            frame = self.draw_center(frame, middle_finger_mcp_center, color=(255,0,0), size=10)
            # frame = cv2.putText(frame, 'click', (10,90), cv2.FONT_HERSHEY_COMPLEX, 1, (0,255,0), 4)
        
        else:
            self.clicking.unhold()
            frame = self.draw_center(frame, middle_finger_mcp_center, color=(0,255,0), size=3)
            # frame = cv2.putText(frame, 'not', (10,90), cv2.FONT_HERSHEY_COMPLEX, 1, (0,0,255), 4)
        frame = cv2.putText(frame, str(self.clicking.sequence), (10,120), cv2.FONT_HERSHEY_COMPLEX, 1, (255,0,0), 4)
        
        
        if middle_finger_mcp_center.y < ring_finger_tip_center.y and middle_finger_mcp_center.y > middle_finger_tip_center.y:
            self.clicking.right_click()
            print('in right click')
        return frame
    
    def update_right_hand(self, frame, index_center):
        frame = self.draw_center(frame, index_center)
        
        screen_size = self.screen_size
        x,y = index_center.x,index_center.y
        
        x = (x -0.5) * screen_size[0] *3
        y = (y -0.3) * screen_size[1] *3
        
        if x < 0: x = self.offset
        elif x > screen_size[0]: x = screen_size[0] - self.offset
        if y < 0: y = self.offset
        elif y > screen_size[1]: y = screen_size[1] - self.offset
        
        frame = cv2.putText(frame, 'x:%d,y:%d'%(x,y), (10,60), cv2.FONT_HERSHEY_COMPLEX, 1, (255,255,0), 4)
        pg.moveTo(x, y) 
        return frame
    def draw_center(self, frame, keypoint, color=(255,0,0), size = 4):
        center = (keypoint.x * self.camera_size[0]), (keypoint.y * self.camera_size[1])
        center = int(center[0]), int(center[1])
        frame = cv2.circle(frame, center, size, color, -1)
        return frame
mp_hands = mp.solutions.hands
offset = 1.5
screen_size = (1920, 1080)
camera_size = (640, 480)
controller = Controller(screen_size, camera_size)
cap = cv2.VideoCapture(0)
cap.set(3,camera_size[0])
cap.set(4,camera_size[1])

def main():
    running = True
    while running:
        suc, frame = cap.read()
        if suc:
            frame = cv2.flip(frame, 1)
            results = hands.process(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
            hand_landmarks = results.multi_hand_landmarks
            if hand_landmarks and len(hand_landmarks) == 2:
                image_height, image_width, _ = frame.shape
                annotated_image = frame.copy()
                for hand_landmark in hand_landmarks:
                    controller.update(frame, hand_landmark)
            cv2.imshow('main',frame)
        key = cv2.waitKey(1)
        if key == ord('a'):
            break
        if key == 32:
            print( len(hand_landmarks))
    cv2.release()
    cv2.destroyAllWindows()
    
if __name__ == '__main__':
    with mp_hands.Hands(
            min_detection_confidence=0.5,
            max_num_hands=2,
            min_tracking_confidence=0.5) as hands:
        main()