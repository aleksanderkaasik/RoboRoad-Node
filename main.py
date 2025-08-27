from flask import Flask, Response
from flask_cors import CORS
from picamera2 import Picamera2
from time import sleep
import cv2

height=720
width=1280

app = Flask(__name__)
CORS(app)
camera = Picamera2()
camera.configure(camera.create_video_configuration(main={"size": (width, height)}))
camera.start()
sleep(2)

def gen_frames():
    while True:
        frame = camera.capture_array("main")
        frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
        ret, buffer = cv2.imencode('.jpg', frame)
        if not ret:
            continue
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + buffer.tobytes() + b'\r\n')
        sleep(1/60) # second per frames

@app.route('/video_feed')
def video_feed():
    return Response(gen_frames(), 
	    mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/')
def index():
    return '<h1>Camera Stream</h1><img src="/video_feed">'

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)