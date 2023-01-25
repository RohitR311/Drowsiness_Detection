import os
import cv2
import time
import streamlit as st
# from pygame import mixer

from drowsy_detection import VideoFrameHandler

def save_file(sound_file):
    with open(os.path.join('audio/', sound_file.name),'wb') as f:
         f.write(sound_file.getbuffer())
    return sound_file.name

video_handler = VideoFrameHandler()

st.set_page_config(
    page_title="Drowsiness Detection",
    page_icon="https://learnopencv.com/wp-content/uploads/2017/12/favicon.png",
    layout="centered",
    initial_sidebar_state="expanded",
    menu_items={
        "About": "Drowsiness detector using MediaPipe",
    },
)

st.title("Drowsiness Detection!")
run = st.checkbox('Run')
uploaded_file = st.file_uploader(' ', type=['wav','mp3'])

FRAME_WINDOW = st.image([], width=400)
camera = cv2.VideoCapture(cv2.CAP_V4L2)
# mixer.init()

if uploaded_file is not None:
    # mixer.music.load(uploaded_file)
    save_file(uploaded_file)

col1, col2 = st.columns(spec=[1, 1])

with col1:
    EAR_THRESH = st.slider("Eye Aspect Ratio threshold:", 0.0, 0.4, 0.18, 0.01)

with col2:
    WAIT_TIME = st.slider(
        "Seconds to wait before sounding alarm:", 0.0, 5.0, 1.0, 0.25)

thresholds = {
    "EAR_THRESH": EAR_THRESH,
    "WAIT_TIME": WAIT_TIME,
}

while run:
    ret, frame = camera.read()
    if ret:
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        frame, play_alarm = video_handler.process(frame, thresholds)

        # if play_alarm and uploaded_file is not None and not mixer.music.get_busy():
        #     time.sleep(0.5)
        #     mixer.music.play()

        FRAME_WINDOW.image(frame)
else:
    st.write('Stopped')

# video_handler = VideoFrameHandler()
# audio_handler = AudioFrameHandler(sound_file_path=alarm_file_path)

# lock = threading.Lock()

# shared_state = {"play_alarm": False}


# def video_frame_callback(frame: av.VideoFrame):
#     frame = frame.to_ndarray(format="bgr24")
#     frame, play_alarm = video_handler.process(frame, thresholds)

#     with lock:
#         shared_state["play_alarm"] = play_alarm

#     return av.VideoFrame.from_ndarray(frame, format="bgr24")


# def audio_frame_callback(frame: av.AudioFrame):
#     with lock:
#         play_alarm = shared_state["play_alarm"]
#     new_frame: av.AudioFrame = audio_handler.process(frame,
#                                                      play_sound=play_alarm)
#     return new_frame


# ctx = webrtc_streamer(
#     key="driver-drowsiness-detection",
#     video_frame_callback=video_frame_callback,
#     audio_frame_callback=audio_frame_callback,
#     rtc_configuration={"iceServers": [
#         {"urls": ["stun:stun.l.google.com:19302"]}]},
#     media_stream_constraints={"video": {"width": True, "audio": True}},
#     video_html_attrs=VideoHTMLAttributes(
#         autoPlay=True, controls=False, muted=False),
# )
