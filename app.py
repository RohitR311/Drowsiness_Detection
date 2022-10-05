from flask import Flask, render_template, request, Response, url_for, redirect
from drowsy_detection import VideoFrameHandler

from pygame import mixer
import cv2
import os

ear_thresh = None
wait_time = None

app = Flask(__name__, template_folder='templates')

alarm_file_path = os.path.join("audio", "wake_up.wav")

video_handler = VideoFrameHandler()

mixer.init()
mixer.music.load(alarm_file_path)

camera = cv2.VideoCapture(0)


def gen(camera):
    global ear_thresh, wait_time
    while True:
        success, frame = camera.read()

        if not success:
            break
        else:
            thresholds = {
                "EAR_THRESH": ear_thresh,
                "WAIT_TIME": wait_time,
            }

            frame, play_alarm = video_handler.process(frame, thresholds)

            if play_alarm and not mixer.music.get_busy():
                mixer.music.play()

            ret, jpeg = cv2.imencode('.jpg', frame)

            frame = jpeg.tobytes()

            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')


@app.route('/', methods=["GET", "POST"])
def index_view():
    global ear_thresh, wait_time

    ear_thresh = request.form.get("ear_thresh")
    wait_time = request.form.get("wait_time")

    if ear_thresh == None and wait_time == None:
        ear_thresh = 0.25
        wait_time = 2.5
    else:
        ear_thresh = float(ear_thresh)
        wait_time = float(wait_time)

    return render_template('index.html', ear_thresh=ear_thresh, wait_time=wait_time)


@app.route('/video_feed')
def video_feed():
    return Response(gen(camera),
                    mimetype='multipart/x-mixed-replace; boundary=frame')


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 33507))
    app.run(debug=True, port=port, host='0.0.0.0')

camera.release()
cv2.destroyAllWindows()
