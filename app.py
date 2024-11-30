from flask import Flask, render_template, jsonify
import sounddevice as sd
from scipy.io.wavfile import write
import threading
import datetime
import os
import numpy as np

app = Flask(__name__)

# Global variables
is_recording = False
recording_data = []
freq = 44100  # Sampling frequency

# Ensure the recordings folder exists
RECORDINGS_FOLDER = 'recordings'
if not os.path.exists(RECORDINGS_FOLDER):
    os.makedirs(RECORDINGS_FOLDER)

def record_audio():
    global recording_data
    recording_data = []  # Clear any previous data
    with sd.InputStream(samplerate=freq, channels=2, dtype='int16', callback=audio_callback):
        while is_recording:
            sd.sleep(100)

def audio_callback(indata, frames, time, status):
    if status:
        print(f"Error: {status}")
    recording_data.append(indata.copy())

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/start_recording', methods=['POST'])
def start_recording():
    global is_recording
    if not is_recording:
        is_recording = True
        threading.Thread(target=record_audio).start()
        return jsonify({"message": "Recording started!"})
    return jsonify({"message": "Already recording!"})

@app.route('/stop_recording', methods=['POST'])
def stop_recording():
    global is_recording
    if is_recording:
        is_recording = False
        filename = f"recording_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.wav"
        filepath = os.path.join(RECORDINGS_FOLDER, filename)  # Save in the recordings folder
        write(filepath, freq, np.concatenate(recording_data))
        return jsonify({"message": f"Recording saved as '{filename}'."})
    return jsonify({"message": "No recording in progress."})

if __name__ == '__main__':
    app.run(debug=True)
