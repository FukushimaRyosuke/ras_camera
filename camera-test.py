import cv2
import requests
import datetime
import time
import smbus
import RPi.GPIO as GPIO

camera = cv2.VideoCapture(0)
cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)

dt_now = datetime.datetime.now()
fps = 20.0
size = (640, 360)
#writer = cv2.VideoWriter('test.m4v', fmt, fps, size)

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
GPIO.setup(17, GPIO.OUT)
GPIO.setup(27, GPIO.IN)

HAAR_FILE = 'haarcascade_frontalface_default.xml'
cascade = cv2.CascadeClassifier(HAAR_FILE)

def get_distance():
    GPIO.output(17, GPIO.LOW)
    GPIO.output(17, True)
    time.sleep(0.00001)
    GPIO.output(17, False)
    while GPIO.input(27) == 0:
        signaloff = time.time()
    while GPIO.input(27) == 1:
        signalon = time.time()
    timepassed = signalon - signaloff
    return timepassed * (331.50 + 00.606681) * 100/2

def line():
    print('send a message to line')
    file_name = 'test.jpg'
    binary=open(file_name, mode='rb')
    files={'imageFile':binary}
    
    line_notify_taken='OBuWXwnj9R8M5vDQjhyXx7aQ080MSw7jz76A8bETgy4'
    line_notify_api='https://notify-api.line.me/api/notify'
    headers={'Authorization':f'Bearer {line_notify_taken}'}
    data={'message':'this is a picture'}
    requests.post(line_notify_api, headers=headers, data=data, files=files)

i = 0
count = 0
wait = 25

avg = None

time.sleep(1)

while True:
    ret, frame = camera.read()
    frame = cv2.resize(frame, size)
    #writer.write(frame)
    #cv2.imshow('frame', frame
    
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    
    if avg is None:
        avg = gray.copy().astype('float')
        continue
    
    cv2.accumulateWeighted(gray, avg, 0.5)
    frameDelta = cv2.absdiff(gray, cv2.convertScaleAbs(avg))
    
    thresh = cv2.threshold(frameDelta, 3, 255, cv2.THRESH_BINARY)[1]
    
    contours = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)[0]

    for target in contours:
        x, y, w, h = cv2.boundingRect(target)
        
        if w < 30: continue
        
        cv2.rectangle(frame, (x, y), (x + w, y + h), (0,255,0), 2)
    
    
    i = i + 1
    if i % 15 == 0:
        distance = get_distance()
        print(distance)
        wait = wait + 1
        
        if (distance > 40 and wait >= 25):
            count == 0
        
        if (distance <= 40 and wait >= 25):
            count = count + 1
    
        if count == 5:
            cv2.imwrite('test.jpg', frame)
            cap.release()
            wait = 0
            line()
            count = 0
          
    if not ret:
        break
    cv2.imshow("Frame", frame)
    key = cv2.waitKey(1)
    if key == 27:
        break
    
#writer.release()
cap.release()
camera.release()
cv2.destroyAllWindows()
#line()


    
    
    