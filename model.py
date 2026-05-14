import cv2
import mediapipe as mp
import math
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL

devices = AudioUtilities.GetSpeakers()
interface = devices.Activate(
    IAudioEndpointVolume._iid_,
    CLSCTX_ALL,
    None
)
volume = cast(interface, POINTER(IAudioEndpointVolume))
volMin, volMax = volume.GetVolumeRange()[:2]
cap = cv2.VideoCapture(0)
mpHands = mp.solutions.hands
hands = mpHands.Hands()
mpDraw = mp.solutions.drawing_utils
while True:
    success, frame = cap.read()
    h, w, c = frame.shape
    results = hands.process(frame)
    thumb_x, thumb_y = 0, 0
    index_x, index_y = 0, 0
    if results.multi_hand_landmarks:
        for handLms in results.multi_hand_landmarks:
            for id, lm in enumerate(handLms.landmark):
                cx = int(lm.x * w)
                cy = int(lm.y * h)
                if id == 4:
                    thumb_x, thumb_y = cx, cy
                if id == 8:
                    index_x, index_y = cx, cy
            cv2.circle(frame,
                       (thumb_x, thumb_y),
                       10,
                       (255, 0, 255),
                       cv2.FILLED)
            cv2.circle(frame,
                       (index_x, index_y),
                       10,
                       (255, 0, 255),
                       cv2.FILLED)
            cv2.line(frame,
                     (thumb_x, thumb_y),
                     (index_x, index_y),
                     (0, 255, 0),
                     3)
            length = math.hypot(
                index_x - thumb_x,
                index_y - thumb_y
            )
            
            vol = volMin + (length / 190) * (volMax - volMin)
            vol = max(volMin, min(vol, volMax))
            volume.SetMasterVolumeLevel(vol, None)
            mpDraw.draw_landmarks(
                frame,
                handLms,
                mpHands.HAND_CONNECTIONS
            )
    cv2.imshow("Volume Controller", frame)
    key = cv2.waitKey(1)
    if key == 27:
        break
cap.release()
cv2.destroyAllWindows()