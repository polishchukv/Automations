import os
import logging
import tkinter as tk
from tkinter import filedialog, messagebox
from dotenv import load_dotenv
import openai as OpenAI
import traceback
import ffmpeg
import threading
from datetime import datetime

# Load environment variables from .env file
load_dotenv()
OpenAI.api_key = os.getenv("OPENAI_API_SIMPLE_TRANSCRIPTION_KEY")  # Placeholder: Replace with your OpenAI API Key
audio_directory = os.getenv("AUDIO_TRANSCRIPTION_DIR")  # Placeholder: Directory for audio files

# Construct file paths for logging and output
log_file_path = os.path.join(audio_directory, "transcription.log")
chunks_dir = os.path.join(audio_directory, "temp_chunks")
output_dir_raw = os.path.join(audio_directory, "Transcripts", "RAW")
output_dir_processed = os.path.join(audio_directory, "Transcripts", "PROCESSED")
raw_dir = os.path.join(audio_directory, "Transcripts", "RAW")

# Setup logging
logging.basicConfig(filename=log_file_path, level=logging.INFO, format='%(asctime)s %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p')

chunk_duration_ms = 15 * 1024 * 1024 * 8 // (192 * 1024) * 1000  # Calculation for chunk size

# Ensure chunks directory exists
if not os.path.exists(chunks_dir):
    logging.warning(f"Creating directory: {chunks_dir}")
    os.makedirs(chunks_dir)

def transcribe_audio(file_path):
    logging.info(f"transcribe_audio function called with file_path: {file_path}")
    try:
        with open(file_path, "rb") as audio_file:
            response = OpenAI.Audio.transcribe(
                model="whisper-1",  # Placeholder model: Adjust as necessary
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
        audio_input = ffmpeg.input(file_path)
        duration = ffmpeg.probe(file_path)['format']['duration']
        chunks = []
        
        start = 0
        while start < float(duration):
            end = start + chunk_duration_ms / 1000
            output_file_path = os.path.join(chunks_dir, f"chunk_{len(chunks)}.mp3")
            (
                ffmpeg
                .input(file_path, ss=start, t=end-start)
                .output(output_file_path, format='mp3')
                .run()
            )
            chunks.append(output_file_path)
            start = end
        logging.info(f"Audio split into {len(chunks)} chunks")
        return chunks
    except Exception as e:
        logging.error(f"Error splitting audio {file_path}: {str(e)}")
        return []

def save_transcription(text, output_file_name):
    output_file_path = os.path.join(output_dir_raw, output_file_name)
    try:
        with open(output_file_path, "w", encoding='utf-8') as f:
            f.write(text)
        logging.info(f"Transcription saved to {output_file_path}")
    except Exception as e:
        logging.error(f"Error saving transcription to {output_file_path}: {str(e)}")

def save_processed_transcription(text, output_file_name):
    output_file_path = os.path.join(output_dir_processed, output_file_name)
    try:
        with open(output_file_path, "w", encoding='utf-8') as f:
            f.write(text)
        logging.info(f"Processed transcription saved to {output_file_path}")
    except Exception as e:
        logging.error(f"Error saving processed transcription to {output_file_path}: {str(e)}")

def select_file():
    file_path = filedialog.askopenfilename(
        filetypes=[("Audio files", "*.mp3;*.wav")],
        title="Select an MP3 or WAV audio file"
    )
    logging.info(f"Selected file: {file_path}")
    
    # Update the StringVar with the path of the selected file
    selected_file_path.set(file_path)
    
    # Enable the process_button after a file is selected
    if file_path:
        process_button.config(state="normal")

def process_file(completion_event):
    file_path = selected_file_path.get()
    print(f"Processing file: {file_path}")
    logging.info(f"Processing file: {file_path}")
    custom_context = custom_prompt_textbox.get("1.0", tk.END).strip() if custom_prompt_var.get() else default_context
    
    if file_path:
        file_size = os.path.getsize(file_path)
        logging.info(f"File size: {file_size}")
        transcriptions = []
        if file_size > 15 * 1024 * 1024:  # 15 MB
            logging.info("File size exceeds 15 MB. Splitting audio into chunks.")
            audio_chunks = split_audio(file_path)
            for chunk_path in audio_chunks:
                logging.info(f"Processing chunk: {chunk_path}")
                transcriptions.append(transcribe_audio(chunk_path))
                os.remove(chunk_path)
        else:
            transcriptions.append(transcribe_audio(file_path))
            
        transcription_text = "\n".join(transcriptions)
        
        # Generate the output file name based on the input file name
        current_date = datetime.now().strftime("%m-%d-%y")
        
        if custom_name_var.get():
            custom_name = custom_name_entry.get().replace(" ", "_")
            output_file_name = f"{custom_name}_{current_date}.txt"
        else:
            output_file_name = f"transcription_{current_date}.txt"
        
        save_transcription(transcription_text, output_file_name)
        post_process_transcript(output_file_name, custom_context)  # Pass custom_context to post_process_transcript
        
        # Signal completion
        completion_event.set()

def post_process_transcript(raw_transcript_file_name, custom_context):
    logging.info(f"Post processing transcript: {raw_transcript_file_name}")
    raw_transcript_path = os.path.join(raw_dir, raw_transcript_file_name)
    
    # Read in raw transcript
    with open(raw_transcript_path, "r") as f:
        raw_transcript = f.read()
        
    # Send the raw transcript to OpenAI for post-processing w/ GPT-4o
    try:
        response = OpenAI.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "system",
                    "content": custom_context
                },
                {
                    "role": "user",
                    "content": raw_transcript
                }
            ]
        )
        summarized_transcript = response.choices[0].message.content
        logging.info(f"Transcript post-processed successfully")
        print("Transcript post-processed successfully.")
        
        # Save the processed transcript
        save_processed_transcription(summarized_transcript, raw_transcript_file_name)
    except Exception as e:
        logging.error(f"Error post-processing transcript: {str(e)}")
        print("Error post-processing transcript.")
        summarized_transcript = ""

def toggle_custom_prompt():
    if custom_prompt_var.get():
        custom_prompt_textbox.pack()
    else:
        custom_prompt_textbox.pack_forget()

def start_processing():
    if custom_name_entry.get() == "":
        messagebox.showerror("Error", "Please enter a custom name.")
        return
    else:
        process_button.config(state="disabled")
        completion_event = threading.Event()
        process_thread = threading.Thread(target=process_file, args=(completion_event,))
        process_thread.start()
        
        def check_completion():
            if completion_event.is_set():
                process_button.config(state="normal")
                print("Transcription process finished.")
                messagebox.showinfo("Success", "Transcription process finished.")
            else:
                root.after(100, check_completion)
        
        check_completion()

# Function to toggle the state of an entry based on a checkbox
def toggle_entry(entry, var):
    if var.get():
        entry.config(state=tk.NORMAL)
    else:
        entry.config(state=tk.DISABLED)

# Default context/prompt
default_context = (

)

root = tk.Tk()
root.title("Audio Transcriber")
root.geometry("700x350")

# Create a StringVar to hold the path of the selected file
selected_file_path = tk.StringVar()
selected_file_path.set("No file selected")

# Create a Label to display the path of the selected file
selected_file_label = tk.Label(root, textvariable=selected_file_path)
selected_file_label.pack()

button_frame = tk.Frame(root)
button_frame.pack()

select_button = tk.Button(button_frame, text="Select an MP3 or WAV file", command=select_file)
select_button.pack(side="right", pady=20)

process_button = tk.Button(button_frame, text="Process Transcript", command=start_processing, state="disabled")
process_button.pack(side="right", pady=20)

custom_prompt_var = tk.IntVar()
custom_prompt_checkbox = tk.Checkbutton(root, text="Use Custom Prompt", variable=custom_prompt_var, command=toggle_custom_prompt)
custom_prompt_checkbox.pack()

custom_prompt_textbox = tk.Text(root, height=10, width=80)
custom_prompt_textbox.pack_forget()  # Hide by default

# Add a checkbox and textbox for custom file naming
custom_name_var = tk.BooleanVar()
custom_name_checkbox = tk.Checkbutton(root, text="Use Custom Name", variable=custom_name_var, command=lambda: toggle_entry(custom_name_entry, custom_name_var))
custom_name_checkbox.pack()

# Add the textbox for the custom name, initially disabled
custom_name_entry = tk.Entry(root)
custom_name_entry.pack()
custom_name_entry.config(state=tk.DISABLED)

root.mainloop()