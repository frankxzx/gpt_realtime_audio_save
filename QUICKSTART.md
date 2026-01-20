# Quick Start Guide

## Overview
This library provides a simple way to capture, combine, and save audio from OpenAI's GPT Realtime API.

## Features
- 🎤 Capture both input and output audio from GPT Realtime sessions
- 🎵 Automatically combine audio into MP3 format
- ☁️ Upload to Azure Blob Storage
- 📊 Track audio statistics (duration, size, etc.)

## Installation

### 1. Install System Dependencies

**Ubuntu/Debian:**
```bash
sudo apt-get update
sudo apt-get install ffmpeg
```

**macOS:**
```bash
brew install ffmpeg
```

**Windows:**
Download from [ffmpeg.org](https://ffmpeg.org/download.html) and add to PATH

### 2. Install Python Dependencies

```bash
pip install -r requirements.txt
```

### 3. Set Up Configuration

```bash
cp config.env.example .env
```

Edit `.env` and add your credentials:
```env
OPENAI_API_KEY=your_api_key_here
AZURE_STORAGE_CONNECTION_STRING=your_connection_string_here
```

## Basic Usage

### Minimal Example

```python
from realtime_audio_handler import RealtimeAudioHandler

# Initialize
handler = RealtimeAudioHandler()

# Add audio as you receive it from the API
# (audio data is PCM16, 24kHz, mono)
handler.add_output_audio_base64(audio_base64_string)

# When done, save as MP3
handler.save_mp3_local("conversation.mp3")
```

### With Blob Upload

```python
import asyncio
from realtime_audio_handler import RealtimeAudioHandler, process_realtime_session

async def main():
    handler = RealtimeAudioHandler(
        blob_connection_string="your_connection_string",
        blob_container="audio-recordings"
    )
    
    # ... add audio chunks as you receive them ...
    
    # Process and upload
    url = await process_realtime_session(handler, upload_to_blob=True)
    print(f"Audio uploaded to: {url}")

asyncio.run(main())
```

### Integration with WebSocket

```python
import json
import websockets
from realtime_audio_handler import RealtimeAudioHandler

async def connect_realtime():
    handler = RealtimeAudioHandler()
    
    url = "wss://api.openai.com/v1/realtime?model=gpt-4o-realtime-preview-2024-12-17"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "OpenAI-Beta": "realtime=v1"
    }
    
    async with websockets.connect(url, extra_headers=headers) as ws:
        async for message in ws:
            event = json.loads(message)
            
            if event["type"] == "response.audio.delta":
                # Capture audio chunk
                handler.add_output_audio_base64(event["delta"])
            
            elif event["type"] == "response.done":
                # Save when complete
                handler.save_mp3_local("conversation.mp3")
                handler.clear_audio()  # Reset for next conversation
```

## Audio Format Details

The GPT Realtime API uses:
- **Format:** PCM16 (16-bit linear PCM)
- **Sample Rate:** 24kHz
- **Channels:** Mono (1 channel)

The handler automatically converts this to MP3 at 128kbps.

## Statistics

Get information about captured audio:

```python
stats = handler.get_stats()
print(f"Input: {stats['input_duration_seconds']}s")
print(f"Output: {stats['output_duration_seconds']}s")
print(f"Total: {stats['total_duration_seconds']}s")
```

## Testing

Run the test suite:

```bash
python test_handler.py
```

All tests should pass if dependencies are correctly installed.

## Troubleshooting

### "ffmpeg not found"
Make sure ffmpeg is installed and in your system PATH.

### "pydub not found"
```bash
pip install pydub
```

### "Azure Storage connection failed"
Check that your connection string is correct and you have network access to Azure.

## Next Steps

- See `example_usage.py` for more examples
- Check the main `README.md` for detailed API documentation
- Review `realtime_audio_handler.py` for the full implementation

## Support

For issues or questions, please open an issue on GitHub.
