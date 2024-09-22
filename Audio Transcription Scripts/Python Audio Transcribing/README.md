# Audio Transcription Script

This script transcribes audio files using the OpenAI API's Whisper model, allowing you to process large audio files by splitting them into manageable chunks, transcribing them, and then post-processing the transcriptions using a custom prompt.

## Prerequisites

- Python 3.x
- Required Python packages:
  - `openai`
  - `ffmpeg-python`
  - `python-dotenv`
  - `tkinter`
  - `logging`
  - `traceback`

Install the required packages using:
```bash
pip install openai ffmpeg-python python-dotenv
```

## How the Script Works

1. **Environment Variables**:
   - Set up your `.env` file with the following entries:
     ```dotenv
     OPENAI_API_SIMPLE_TRANSCRIPTION_KEY=your_openai_api_key
     AUDIO_TRANSCRIPTION_DIR=/path/to/audio/transcriptions
     ```

2. **Transcribing Audio**:
   - The script loads the audio file, transcribes it using OpenAI's `whisper-1` model, and logs the process.
   - If the audio file exceeds 15 MB, it splits the file into chunks and processes each chunk individually.

3. **Saving Transcriptions**:
   - Transcriptions are saved as text files in the directories specified by `AUDIO_TRANSCRIPTION_DIR`.

## How to Use the Script

1. Ensure you have set up your `.env` file with the correct `OPENAI_API_KEY` and `AUDIO_TRANSCRIPTION_DIR`.
2. Run the script:
   ```bash
   python script_name.py
   ```
3. The graphical user interface (GUI) will allow you to:
   - Select an audio file (`.mp3` or `.wav`).
   - Choose to use a custom prompt or custom file name for the transcription.

## Potential Improvements

- **Error Handling**: The script can be enhanced by handling potential network errors, file read/write errors, and API exceptions more gracefully.
- **Multi-threading**: Consider improving the script's responsiveness and performance by implementing more efficient threading, especially for long-running transcriptions.
- **Output Formatting**: Introduce options for output formatting to meet specific user requirements or preferences.

## Known Issues

- The script currently only processes `mp3` and `wav` files. Support for additional file formats could be implemented using `ffmpeg`.
- Large files may take longer to process, so it's recommended to use chunking for files larger than 15 MB.

## Disclaimer

- This script requires a valid OpenAI API key and is intended for transcription purposes. Ensure compliance with OpenAI's terms of service and local regulations regarding data privacy and usage.