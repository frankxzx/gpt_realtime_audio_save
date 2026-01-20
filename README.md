# GPT Realtime Audio Save

A Python library for capturing, processing, and storing audio from OpenAI's GPT Realtime API. This tool captures both input and output audio streams, synthesizes them into MP3 format, and uploads the result to Azure Blob Storage.

## Features

- 🎤 Capture input audio from user
- 🔊 Capture output audio from GPT Realtime API
- 🎵 Synthesize audio streams into MP3 format
- ☁️ Upload to Azure Blob Storage
- 📊 Audio statistics and duration tracking
- 🔄 Async/await support for modern Python applications

## Installation

1. Clone this repository:
```bash
git clone https://github.com/frankxzx/gpt_realtime_audio_save.git
cd gpt_realtime_audio_save
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Install ffmpeg (required by pydub for audio processing):
   - **Ubuntu/Debian**: `sudo apt-get install ffmpeg`
   - **macOS**: `brew install ffmpeg`
   - **Windows**: Download from [ffmpeg.org](https://ffmpeg.org/download.html)

## Configuration

1. Copy the example configuration file:
```bash
cp config.env.example .env
```

2. Edit `.env` and add your credentials:
```bash
OPENAI_API_KEY=your_openai_api_key_here
AZURE_STORAGE_CONNECTION_STRING=your_azure_connection_string_here
```

## Usage

### Basic Usage

```python
from realtime_audio_handler import RealtimeAudioHandler, process_realtime_session
import asyncio

# Initialize the handler
handler = RealtimeAudioHandler(
    blob_connection_string="your_connection_string",
    blob_container="audio-recordings"
)

# Add audio data (from GPT Realtime API)
handler.add_output_audio_base64(audio_base64_from_api)

# Process and upload when done
result = await process_realtime_session(handler, upload_to_blob=True)
print(f"Audio uploaded to: {result}")
```

### Integration with GPT Realtime API

```python
import json
import websockets
from realtime_audio_handler import RealtimeAudioHandler, process_realtime_session

async def handle_realtime_session(api_key):
    # Initialize audio handler
    handler = RealtimeAudioHandler()
    
    # Connect to OpenAI Realtime API
    url = "wss://api.openai.com/v1/realtime?model=gpt-4o-realtime-preview-2024-12-17"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "OpenAI-Beta": "realtime=v1"
    }
    
    async with websockets.connect(url, extra_headers=headers) as websocket:
        async for message in websocket:
            event = json.loads(message)
            
            # Capture output audio
            if event["type"] == "response.audio.delta":
                handler.add_output_audio_base64(event["delta"])
            
            # When response is complete, save audio
            elif event["type"] == "response.done":
                result = await process_realtime_session(handler)
                print(f"Saved audio: {result}")
                handler.clear_audio()  # Start fresh for next conversation
```

### Save Locally (Without Blob Upload)

```python
handler = RealtimeAudioHandler()

# Add your audio data
# handler.add_input_audio(input_bytes)
# handler.add_output_audio(output_bytes)

# Save to local file
filepath = handler.save_mp3_local("conversation.mp3")
print(f"Saved to: {filepath}")
```

### Get Audio Statistics

```python
stats = handler.get_stats()
print(f"Input duration: {stats['input_duration_seconds']}s")
print(f"Output duration: {stats['output_duration_seconds']}s")
print(f"Total duration: {stats['total_duration_seconds']}s")
```

## API Reference

### RealtimeAudioHandler

Main class for handling audio capture and processing.

#### Methods

- `add_input_audio(audio_data: bytes)` - Add raw input audio bytes
- `add_output_audio(audio_data: bytes)` - Add raw output audio bytes
- `add_input_audio_base64(audio_base64: str)` - Add base64-encoded input audio
- `add_output_audio_base64(audio_base64: str)` - Add base64-encoded output audio
- `synthesize_mp3(sample_rate: int = 24000, channels: int = 1) -> bytes` - Generate MP3 from captured audio
- `save_mp3_local(filename: str = None) -> str` - Save MP3 locally
- `upload_to_blob(blob_name: str = None) -> str` - Upload MP3 to Azure Blob Storage
- `clear_audio()` - Clear all captured audio chunks
- `get_stats() -> dict` - Get statistics about captured audio

## Audio Format

The GPT Realtime API uses:
- **Format**: PCM16 (16-bit linear PCM)
- **Sample Rate**: 24kHz (24000 Hz)
- **Channels**: Mono (1 channel)

The synthesized MP3 uses:
- **Bitrate**: 128 kbps
- **Format**: MP3
- **Structure**: Input audio → 500ms silence → Output audio

## Requirements

- Python 3.8+
- pydub
- azure-storage-blob
- websockets
- ffmpeg (system dependency)

## Examples

See `example_usage.py` for complete examples including:
- WebSocket connection to OpenAI Realtime API
- Audio capture and processing
- Local file handling
- Integration snippets

## Troubleshooting

### "pydub requires ffmpeg"
Install ffmpeg on your system (see Installation section).

### "Azure Storage connection string not provided"
Make sure you've set the `AZURE_STORAGE_CONNECTION_STRING` environment variable or passed it to the constructor.

### Audio quality issues
Ensure you're using the correct sample rate (24000 Hz) and format (PCM16) when adding audio data.

## License

MIT License

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
