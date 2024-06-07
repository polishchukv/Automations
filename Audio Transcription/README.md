# Audio Transcription and Processing Tool

This project is an audio transcription tool built using Python. It provides functionality to split audio files into chunks, transcribe these chunks using OpenAI's Whisper model, and process the transcripts with OpenAI's GPT-4 model to generate summaries and key takeaways. The tool includes a graphical user interface (GUI) for selecting and processing audio files.

## Features

- **Audio Splitting**: Splits large audio files into smaller chunks.
- **Transcription**: Uses OpenAI's Whisper model to transcribe audio files into text.
- **Post-processing**: Processes raw transcripts to generate summaries and key takeaways using OpenAI's GPT-4 model.
- **Graphical User Interface**: Provides a simple GUI for selecting and processing audio files.

## Requirements

- Python 3.8+
- Libraries: `os`, `logging`, `tkinter`, `pydub`, `dotenv`, `openai`

## Setup

### Prerequisites

1. **Install required libraries**:
    ```bash
    pip install os logging tkinter pydub python-dotenv openai
    ```

2. **Environment Variables**:
    - Create a `.env` file in the project directory and add the following variables:
      ```env
      OPENAI_API_SIMPLE_TRANSCRIPTION_KEY=your_openai_api_key
      AUDIO_TRANSCRIPTION_DIR=your_audio_directory
      ```

### Directory Structure

Ensure the following directories exist within your audio directory:
- `Transcripts/RAW`: Directory to store raw transcripts.
- `Transcripts/PROCESSED`: Directory to store processed transcripts.
- `temp_chunks`: Directory to store temporary audio chunks.

### Logging

- The tool logs its operations to `transcription.log` in the specified audio directory.

## Usage

### Running the GUI

Run the script to launch the graphical user interface:
```bash
python simple_transcription.py
```

## GUI Operations

### Select an MP3 file
Click on "Select an MP3 file" to choose the audio file you want to process.

### Process Transcript
After selecting a file, click on "Process Transcript" to start the transcription and processing.

## Functions

### `transcribe_audio(file_path)`

Transcribes the audio file at the given path using OpenAI's Whisper model.

- **Parameters**: 
  - `file_path` (str): Path to the audio file.
- **Returns**: 
  - Transcribed text or an empty string in case of an error.

### `split_audio(file_path)`

Splits the audio file at the given path into smaller chunks for easier processing.

- **Parameters**: 
  - `file_path` (str): Path to the audio file.
- **Returns**: 
  - List of file paths to the created audio chunks.

### `save_transcription(transcription, file_name)`

Saves the transcription to a specified file.

- **Parameters**: 
  - `transcription` (str): The transcribed text.
  - `file_name` (str): Name of the file to save the transcription.

### `process_transcript(raw_transcript_file_name)`

Processes the raw transcript using OpenAI's GPT-4 model to generate summaries and key takeaways.

- **Parameters**: 
  - `raw_transcript_file_name` (str): Name of the raw transcript file.

## Logging

The tool logs the following events:
- Directory creation
- Function calls (`transcribe_audio`, `split_audio`, `save_transcription`, `process_transcript`)
- Success and error messages for transcription and post-processing

## Error Handling

The tool logs errors and exceptions to the log file, including traceback information to help with debugging.
