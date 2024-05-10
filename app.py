from flask import Flask, jsonify, render_template, request, send_file, url_for
import pyaudio
import wave
import threading
import speech_recognition as sr
import google.generativeai as genai
from gtts import gTTS
import os


app = Flask(__name__)
YOUR_API_KEY = "AIzaSyCyfSUy6fb8xM10P296xFljrQAsHDpIVm4"
# Global variables for audio recording
RECORDING = False
output_filename = "recorded_audio.wav"

def record_audio(output_filename, duration=5, chunk=1024, format=pyaudio.paInt16, channels=1, rate=44100):
    global RECORDING
    audio = pyaudio.PyAudio()

    # Open stream
    stream = audio.open(format=format, channels=channels, rate=rate,
                        input=True, frames_per_buffer=chunk)

    # print("Recording...")

    frames = []

    # Record audio
    while RECORDING:
        data = stream.read(chunk)
        frames.append(data)

    # print("Finished recording.")

    # Stop stream
    stream.stop_stream()
    stream.close()
    audio.terminate()

    # Save the recorded audio as a WAV file
    wf = wave.open(output_filename, 'wb')
    wf.setnchannels(channels)
    wf.setsampwidth(audio.get_sample_size(format))
    wf.setframerate(rate)
    wf.writeframes(b''.join(frames))
    wf.close()


def convert_audio_to_text(audio_file):
    recognizer = sr.Recognizer()
    with sr.AudioFile(audio_file) as source:
        audio_data = recognizer.record(source)
        text = recognizer.recognize_google(audio_data)
    return text

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/start_record', methods=['POST'])
def start_record():
    global RECORDING
    RECORDING = True
    t = threading.Thread(target=record_audio, args=(output_filename,))
    t.start()
    return "Recording Started!"

@app.route('/stop_record', methods=['POST'])
def stop_record():
    global RECORDING
    RECORDING = False

    recognizer = sr.Recognizer()
    with sr.AudioFile("recorded_audio.wav") as audio:
        audio_data_text = recognizer.record(audio)
        ouput_text = recognizer.recognize_google(audio_data_text)
    
    return "User: " + " " +ouput_text


@app.route('/convert_recording_to_text', methods=['POST'])
def convert_recording_to_text():
    output_filename = "recorded_audio.wav"
    text = convert_audio_to_text(output_filename)
    genai.configure(api_key=YOUR_API_KEY)
    model = genai.GenerativeModel('gemini-1.0-pro-latest')
    response = model.generate_content(text)
    language = 'en'
    tts = gTTS(response.text, lang=language, slow=False)
    # tts.save("sample.mp3")
    filename = "sample.mp3"
    filepath = os.path.join("static", filename)
    tts.save(filepath)
    # os.system("start sample.mp3")
    return response.text
    

if __name__ == '__main__':
    app.run(debug=True)

#inital Commit
