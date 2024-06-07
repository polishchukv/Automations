import os
import logging
import tkinter as tk
from tkinter import filedialog, messagebox
from pydub import AudioSegment
from dotenv import load_dotenv
import openai as OpenAI
import traceback

# Load environment variables from .env file
load_dotenv()
OpenAI.api_key = os.getenv("OPENAI_API_SIMPLE_TRANSCRIPTION_KEY")
audio_directory = os.getenv("AUDIO_TRANSCRIPTION_DIR")

# Use os.path.join to create the full paths
log_file_path = os.path.join(audio_directory, "transcription.log")
chunks_dir = os.path.join(audio_directory, "temp_chunks")
output_dir_raw = os.path.join(audio_directory, "Transcripts", "RAW")
output_dir_processed = os.path.join(audio_directory, "Transcripts", "PROCESSED")
raw_dir = os.path.join(audio_directory, "Transcripts", "RAW")

# Setup logging
logging.basicConfig(filename=log_file_path, level=logging.INFO, format='%(asctime)s %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p')

chunk_duration_ms = 15 * 1024 * 1024 * 8 // (192 * 1024) * 1000  # 15 MB in duration (ms) assuming 192 kbps bitrate

# Ensure chunks_dir exists
if not os.path.exists(chunks_dir):
    logging.warning(f"Creating directory: {chunks_dir}")
    os.makedirs(chunks_dir)

def transcribe_audio(file_path):
    logging.info(f"transcribe_audio function called with file_path: {file_path}")
    # Transcription using whisper-1 model
    try:
        with open(file_path, "rb") as audio_file:
            response = OpenAI.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file,
                response_format="text"
            )
        logging.info(f"Transcription successful for {file_path}")
        return response
    except Exception as e:
        logging.error(f"Error transcribing {file_path}: {str(e)}\n{traceback.format_exc()}")
        return ""

def split_audio(file_path):
    logging.info("split_audio function called")
    try:
        audio = AudioSegment.from_mp3(file_path)
        chunks = []
        start = 0
        
        # Split audio into chunks of the calculated duration
        while start < len(audio):
            end = start + chunk_duration_ms
            chunks.append(audio[start:end])
            start = end
        logging.info(f"Audio split into {len(chunks)} chunks")
        return chunks
    except Exception as e:
        logging.error(f"Error splitting audio {file_path}: {str(e)}")
        return []

def save_transcription(text, output_file_name):
    output_file_path = os.path.join(output_dir_raw, output_file_name)
    try:
        with open(output_file_path, "w") as f:
            f.write(text)
        logging.info(f"Transcription saved to {output_file_path}")
    except Exception as e:
        logging.error(f"Error saving transcription to {output_file_path}: {str(e)}")

def save_processed_transcription(text, output_file_name):
    output_file_path = os.path.join(output_dir_processed, output_file_name)
    try:
        with open(output_file_path, "w") as f:
            f.write(text)
        logging.info(f"Processed transcription saved to {output_file_path}")
    except Exception as e:
        logging.error(f"Error saving processed transcription to {output_file_path}: {str(e)}")

def select_file():
    file_path = filedialog.askopenfilename(
        filetypes=[("MP3 files", "*.mp3")],
        title="Select an MP3 audio file"
    )
    logging.info(f"Selected file: {file_path}")
    
    # Update the StringVar with the path of the selected file
    selected_file_path.set(file_path)
    
    # Enable the process_button after a file is selected
    if file_path:
        process_button.config(state="normal")
    
def process_file():
    file_path = selected_file_path.get()
    
    if file_path:
        file_size = os.path.getsize(file_path)
        logging.info(f"File size: {file_size}")
        transcriptions = []
        if file_size > 15 * 1024 * 1024:  # 15 MB
            logging.info("File size exceeds 15 MB. Splitting audio into chunks.")
            audio_chunks = split_audio(file_path)
            for i, chunk in enumerate(audio_chunks):
                chunk_path = os.path.join(chunks_dir, f"chunk_{i}.mp3")
                chunk.export(chunk_path, format="mp3")
                logging.info(f"Chunk saved to {chunk_path}")
                transcriptions.append(transcribe_audio(chunk_path))
                os.remove(chunk_path)
        else:
            transcriptions.append(transcribe_audio(file_path))
            
        transcription_text = "\n".join(transcriptions)
        
        # Generate the output file name based on the input file name
        output_file_name = os.path.basename(file_path)
        output_file_name = os.path.splitext(output_file_name)[0] + ".txt"
        
        save_transcription(transcription_text, output_file_name)
        post_process_transcript(output_file_name)  # Call post_process_transcript after saving the raw transcript

        
def post_process_transcript(raw_transcript_file_name):
    logging.info(f"Post processing transcript: {raw_transcript_file_name}")
    raw_transcript_path = os.path.join(raw_dir, raw_transcript_file_name)
    
    # Read in raw transcript
    with open(raw_transcript_path, "r") as f:
        raw_transcript = f.read()
        
    # Send the raw transcript to OpenAI for post-processing w/ GPT-4o
    try:
        response = OpenAI.chat.completions.create(
            model = "gpt-4o",
            messages = [
                {
                    "role": "system",
                    "content": "You are a helpful assistant that summarizes long text transcripts and then provides key takeaway points. Your task is to read through any transcript passed in, and provide both a detailed summary of the contents as well as the key takeaway points."
                },
                {
                    "role": "user",
                    "content": raw_transcript
                }
            ]
        )
        summarized_transcript = response.choices[0].message.content
        logging.info(f"Transcript post-processed successfully")
        
        # Save the processed transcript
        save_processed_transcription(summarized_transcript, raw_transcript_file_name)
    except Exception as e:
        logging.error(f"Error post-processing transcript: {str(e)}")
        summarized_transcript = ""
    
# GUI Setup
root = tk.Tk()
root.title("Audio Transcriber")
root.geometry("700x100")

# Create a StringVar to hold the path of the selected file
selected_file_path = tk.StringVar()
selected_file_path.set("No file selected")

# Create a Label to display the path of the selected file
selected_file_label = tk.Label(root, textvariable=selected_file_path)
selected_file_label.pack()

button_frame = tk.Frame(root)
button_frame.pack()

select_button = tk.Button(button_frame, text="Select an MP3 file", command=select_file)
select_button.pack(side="right", pady=20)

process_button = tk.Button(button_frame, text="Process Transcript", command=process_file, state="disabled")
process_button.pack(side="right", pady=20)

root.mainloop()
