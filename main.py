from flask import Flask, Response
from flask_cors import CORS
from picamera2 import Picamera2
from time import sleep
import cv2

import psutil
import shutil
import platform
import os

height=720
width=1280

app = Flask(__name__)
CORS(app)
camera = Picamera2()
camera.configure(camera.create_video_configuration(main={"size": (width, height)}))
camera.start()

def dataConversionMeasurement(size_in_bytes):
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if size_in_bytes < 1024.0:
            return f"{size_in_bytes:.2f} {unit}"
        size_in_bytes /= 1024.0
    return f"{size_in_bytes:.2f} PB"

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

@app.route('/system_info')
def system_info():
    cpuPercentage  = round(psutil.cpu_percent(interval=1), 2)
    cpuCore = psutil.cpu_count(logical=True)
    
    virtual_mem = psutil.virtual_memory()
    ramTotal = virtual_mem.total
    ramUsed = virtual_mem.used
    ramPercentage  = round(virtual_mem.percent, 2)
    ramTotal = dataConversionMeasurement(ramTotal)
    ramUsed = dataConversionMeasurement(ramUsed)

    disk = shutil.disk_usage("/")
    diskTotal = disk.total
    diskUsed = disk.used
    diskPercentage  = round((diskUsed / diskTotal) * 100, 2)
    
    diskTotal = dataConversionMeasurement(diskTotal)
    diskUsed = dataConversionMeasurement(diskUsed)

    uptime = os.popen('uptime -p').read().strip()

    return {
        "cpu": {
            "percent": cpuPercentage,
            "cores": cpuCore
        },
        "ram": {
            "total": ramTotal,
            "used": ramUsed,
            "percent": ramPercentage 
        },
        "disk": {
            "total": diskTotal,
            "used": diskUsed,
            "percent": diskPercentage 
        },
        "uptime": uptime,
    }

@app.route('/video_feed')
def video_feed():
    return Response(gen_frames(), 
	    mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/')
def index():
    return '<h1>Camera Stream</h1><img src="/video_feed">'

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)