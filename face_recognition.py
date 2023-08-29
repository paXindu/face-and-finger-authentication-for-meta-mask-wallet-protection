from flask import Flask, render_template, request, session, redirect, url_for, Response, jsonify
import mysql.connector
import cv2
from PIL import Image
import numpy as np
import os
import time
from datetime import date
import json


from printId import print_nic 
 
app = Flask(__name__)
 
cnt = 0
pause_cnt = 0
justscanned = False

 
mydb = mysql.connector.connect(
    host="localhost",
    user="root",
    passwd="root",
    database="voters"
)
mycursor = mydb.cursor()  




def face_recognition():  # generate frame by frame from camera
    def draw_boundary(img, classifier, scaleFactor, minNeighbors, color, text, clf):
        gray_image = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        features = classifier.detectMultiScale(gray_image, scaleFactor, minNeighbors)
 
        global justscanned
        global pause_cnt
        global voter_nic
        
 
        pause_cnt += 1
 
        coords = []
 
        for (x, y, w, h) in features:
            cv2.rectangle(img, (x, y), (x + w, y + h), color, 2)
            id, pred = clf.predict(gray_image[y:y + h, x:x + w])
            confidence = int(100 * (1 - pred / 300))
            cv2.putText(img, str(int(confidence))+' %', (x + 20, y + h + 28), cv2.FONT_HERSHEY_SCRIPT_SIMPLEX, 0.9, (153, 255, 255), 2)
            if confidence > 75 and not justscanned:
                global cnt
                cnt += 1
 
                
                w_filled = (cnt / 30) * w
 
                
 
                cv2.rectangle(img, (x, y + h + 40), (x + w, y + h + 50), color, 2)
                cv2.rectangle(img, (x, y + h + 40), (x + int(w_filled), y + h + 50), (153, 255, 255), cv2.FILLED)
 
                mycursor.execute("select a.img_person, b.voter_name"
                                 "  from img_dataset a "
                                 "  left join voters b on a.img_person = b.voter_nic "
                                 " where img_id = " + str(id))
                row = mycursor.fetchone()
                voter_nic = row[0]

                
                
                
 
                if int(cnt) == 30:
                    cnt = 0
 
                    mycursor.execute("insert into voters_auth (auth_date, auth_voter) values('"+str(date.today())+"', '" + voter_nic + "')")
                    mydb.commit()
 
                    justscanned = True
                    pause_cnt = 0

                    print_nic(voter_nic)
                        

                    cap.release()
                    cv2.destroyAllWindows()
                    
 
            else:
                if not justscanned:
                    cv2.putText(img, 'UNKNOWN', (x, y - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2, cv2.LINE_AA)
                else:
                    cv2.putText(img, ' ', (x, y - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2,cv2.LINE_AA)
 
                if pause_cnt > 80:
                    justscanned = False
 
            coords = [x, y, w, h]
        return coords
 
    def recognize(img, clf, faceCascade):
        coords = draw_boundary(img, faceCascade, 1.1, 10, (255, 255, 0), "Face", clf)
        return img
 
    faceCascade = cv2.CascadeClassifier("./resources/haarcascade_frontalface_default.xml")
    clf = cv2.face.LBPHFaceRecognizer_create()
    clf.read("classifier.xml")
 
    wCam, hCam = 400, 400
 
    cap = cv2.VideoCapture(0)
    cap.set(3, wCam)
    cap.set(4, hCam)
 
    while True:
        ret, img = cap.read()
        img = recognize(img, clf, faceCascade)
 
        frame = cv2.imencode('.jpg', img)[1].tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')
        
        
        
 
        key = cv2.waitKey(1)
        if key == 27:
            break

        
        
 