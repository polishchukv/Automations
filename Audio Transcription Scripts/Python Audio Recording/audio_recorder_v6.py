import os
import pyaudiowpatch as pyaudio
import wave
import threading
import time
import gc
from datetime import datetime
from pydub import AudioSegment
from pydub.silence import detect_silence
from dotenv import load_dotenv

load_dotenv(override=True)

# Folder to save recordings (source from .env file)
SAVE_FOLDER = os.getenv("RECORDER_SAVE_FOLDER")

# Ensure the save folder exists
if not os.path.exists(SAVE_FOLDER):
    os.makedirs(SAVE_FOLDER)

# Parameters
FORMAT = pyaudio.paInt24  # Audio format (24-bit PCM)
CHANNELS = 2              # Number of channels (stereo)
CHUNK = 512               # Chunk size (number of frames per buffer)

# Generate timestamp for the output file name
timestamp = datetime.now().strftime("%d-%m-%Y_%H-%M-%S")
OUTPUT_FILENAME = os.path.join(SAVE_FOLDER, f"audio_recording_{timestamp}.wav")
PROCESSED_FILENAME = os.path.join(SAVE_FOLDER, f"audio_recording_{timestamp}_processed.wav")

# Create an interface to PortAudio
audio = pyaudio.PyAudio()

# Find the loopback device (This is platform-specific; generalized for documentation)
try:
    wasapi_info = audio.get_host_api_info_by_type(pyaudio.paWASAPI)
except OSError:
    raise RuntimeError("WASAPI is not available on this system.")

# Select default output device (Replace with a dynamic configuration if possible)
default_speakers = audio.get_device_info_by_index(wasapi_info["defaultOutputDevice"])

# Check for loopback device availability
if not default_speakers["isLoopbackDevice"]:
    for loopback in audio.get_loopback_device_info_generator():
        if default_speakers["name"] in loopback["name"]:
            default_speakers = loopback
            break
    else:
        raise RuntimeError("Default loopback output device not found.")

# Open a stream to the loopback device
stream = audio.open(format=FORMAT,
                    channels=default_speakers["maxInputChannels"],
                    rate=int(default_speakers["defaultSampleRate"]),
                    input=True,
                    input_device_index=default_speakers["index"],
                    frames_per_buffer=CHUNK)

print(f"Recording from: ({default_speakers['index']}) {default_speakers['name']}")

stop_recording = False
pause_recording = False

# Function to record data in chunks
def record():
    total_data_size_gc = 0  # Track total data size recorded
    try:
        with wave.open(OUTPUT_FILENAME, 'wb') as wf:
            wf.setnchannels(default_speakers["maxInputChannels"])
            wf.setsampwidth(audio.get_sample_size(FORMAT))
            wf.setframerate(int(default_speakers["defaultSampleRate"]))

            while not stop_recording:
                if pause_recording:
                    time.sleep(0.1)
                    continue
                data = stream.read(CHUNK)
                wf.writeframes(data)
                total_data_size_gc += len(data)

                # Force garbage collection periodically
                if total_data_size_gc >= 50 * 1024 * 1024:
                    gc.collect()
                    total_data_size_gc = 0
    except Exception as e:
        print(f"An error occurred while recording: {str(e)}")

try:
    recording_thread = threading.Thread(target=record)
    recording_thread.start()

    # User commands to control the recording
    while True:
        command = input().strip().upper()
        if command == "STOP":
            stop_recording = True
            break
        elif command == "PAUSE":
            pause_recording = True
            print("Recording paused.")
        elif command == "RESUME":
            pause_recording = False
            print("Recording resumed.")

    print("Finished recording.")
finally:
    # Properly close the stream
    if stream.is_active():
        stream.stop_stream()
    stream.close()
    audio.terminate()
    print("Audio interface terminated.")

# Load recorded file with pydub
audio_segment = AudioSegment.from_wav(OUTPUT_FILENAME)
print(f"Loaded audio from {OUTPUT_FILENAME}")

# Detect silent segments
silent_ranges = detect_silence(audio_segment, min_silence_len=500, silence_thresh=-40)

# Process non-silent segments
nonsilent_ranges = []
if silent_ranges:
    previous_end = 0
    for start, end in silent_ranges:
        if previous_end != start:
            nonsilent_ranges.append([previous_end, start])
        previous_end = end
    if previous_end < len(audio_segment):
        nonsilent_ranges.append([previous_end, len(audio_segment)])
else:
    nonsilent_ranges = [[0, len(audio_segment)]]

# Combine non-silent segments
processed_audio = AudioSegment.empty()
for start, end in nonsilent_ranges:
    processed_audio += audio_segment[start:end]

# Export the processed audio
processed_audio.export(PROCESSED_FILENAME, format="wav", parameters=["-ac", str(CHANNELS), "-ar", str(int(default_speakers["defaultSampleRate"]))])
print(f"Processed audio saved to {PROCESSED_FILENAME}")
