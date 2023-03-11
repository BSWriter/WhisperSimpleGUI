# Run the GUI loop
# root.mainloop()
import tkinter as tk
import threading
import speech_recognition as sr
import whisper
import pyaudio
import pyttsx3
import wave

FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100
CHUNK = 1024
RECORD_SECONDS = 5
WAVE_OUTPUT_FILENAME = "output.wav"


model = whisper.load_model("base")


# Create the GUI window
root = tk.Tk()
root.geometry("800x600") # Set the window size

# Initialize the Text to Speech engine
engine = pyttsx3.init()
# Sets the rate and volume of the speech
engine.setProperty('rate', 150) 
engine.setProperty('volume', 0.7) 
# Set the voice to a female voice
voices = engine.getProperty('voices')
engine.setProperty('voice', voices[1].id)

# Add a label to the GUI
label = tk.Label(root, text="Press the button to start speaking")
label.pack()

# Add a button to the GUI
button = tk.Button(root, text="Click me!")
button.pack()

# Define a function to handle the button click
def handle_button_click():
    # Disable the button while processing speech
    button.config(state=tk.DISABLED)

    # Change the label text to indicate that speech is being processed
    label.config(text="Processing speech...")

    # Create a new thread for the speech recognition process
    speech_thread = threading.Thread(target=process_speech)
    speech_thread.start()

# Speech to Text
def process_speech():
    audio = pyaudio.PyAudio()
    # open microphone stream
    stream = audio.open(format=FORMAT, channels=CHANNELS,
                    rate=RATE, input=True,
                    frames_per_buffer=CHUNK)
    frames = []

    root.after(0, label.config, {'text': "Recording..."})

    # record for the specified number of seconds
    for i in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
        data = stream.read(CHUNK)
        frames.append(data)

    # stop the stream and close the audio device
    stream.stop_stream()
    stream.close()
    audio.terminate()

    # save the recorded data as a wave file
    wf = wave.open(WAVE_OUTPUT_FILENAME, 'wb')
    wf.setnchannels(CHANNELS)
    wf.setsampwidth(audio.get_sample_size(FORMAT))
    wf.setframerate(RATE)
    wf.writeframes(b''.join(frames))
    wf.close()

    root.after(0, label.config, {'text': "Transcribing Text..."})
    result = model.transcribe("output.wav", fp16=False)
    root.after(0, label.config, {'text': "You said: "+result["text"]})
    speak_output(result["text"])
    root.after(0, button.config, {'state': tk.NORMAL})

# Text to Speech
def speak_output(output):
    # Convert the text to speech
    engine.say(output)

    # Run the engine and wait for the speech to complete
    engine.runAndWait()

# Add the handle_button_click function to the button's command
button.config(command=handle_button_click)

# Run the GUI loop
root.mainloop()

