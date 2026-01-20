"""
Example usage of RealtimeAudioHandler with OpenAI Realtime API
This demonstrates how to integrate audio capture with the GPT Realtime API
"""

import asyncio
import json
import os
from realtime_audio_handler import RealtimeAudioHandler, process_realtime_session

try:
    import websockets
except ImportError:
    websockets = None


async def connect_to_realtime_api(api_key: str, handler: RealtimeAudioHandler):
    """
    Connect to OpenAI Realtime API and handle audio
    
    Args:
        api_key: OpenAI API key
        handler: RealtimeAudioHandler instance
    """
    if websockets is None:
        raise ImportError("websockets is required. Install with: pip install websockets")
    
    url = "wss://api.openai.com/v1/realtime?model=gpt-4o-realtime-preview-2024-12-17"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "OpenAI-Beta": "realtime=v1"
    }
    
    async with websockets.connect(url, extra_headers=headers) as websocket:
        print("Connected to OpenAI Realtime API")
        
        # Configure session
        session_config = {
            "type": "session.update",
            "session": {
                "modalities": ["text", "audio"],
                "instructions": "You are a helpful assistant.",
                "voice": "alloy",
                "input_audio_format": "pcm16",
                "output_audio_format": "pcm16",
                "input_audio_transcription": {
                    "model": "whisper-1"
                },
                "turn_detection": {
                    "type": "server_vad",
                    "threshold": 0.5,
                    "prefix_padding_ms": 300,
                    "silence_duration_ms": 200
                }
            }
        }
        await websocket.send(json.dumps(session_config))
        
        # Message handling loop
        try:
            async for message in websocket:
                event = json.loads(message)
                event_type = event.get("type")
                
                # Handle input audio events
                if event_type == "input_audio_buffer.committed":
                    print("Input audio committed")
                    
                elif event_type == "conversation.item.input_audio_transcription.completed":
                    transcript = event.get("transcript", "")
                    print(f"User said: {transcript}")
                    
                # Handle output audio events
                elif event_type == "response.audio.delta":
                    # Output audio chunk
                    audio_base64 = event.get("delta", "")
                    if audio_base64:
                        handler.add_output_audio_base64(audio_base64)
                        
                elif event_type == "response.audio.done":
                    print("Output audio completed")
                    
                elif event_type == "response.done":
                    print("Response completed")
                    # At this point, both input and output audio should be captured
                    
                elif event_type == "error":
                    print(f"Error: {event.get('error', {})}")
                    
        except websockets.exceptions.ConnectionClosed:
            print("Connection closed")


async def example_realtime_session():
    """
    Example of a complete realtime session with audio capture
    """
    # Get API key from environment
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("Please set OPENAI_API_KEY environment variable")
        return
        
    # Initialize handler
    handler = RealtimeAudioHandler()
    
    # Simulate audio capture (in real usage, this would come from the API)
    # For demonstration, we'll use mock data
    print("Starting realtime session...")
    print("Note: This is a mock example. In production, audio would come from the API.")
    
    # Mock: Add some audio data (in real usage, this comes from the API)
    # handler.add_input_audio(input_audio_bytes)
    # handler.add_output_audio(output_audio_bytes)
    
    # For actual API connection, uncomment:
    # await connect_to_realtime_api(api_key, handler)
    
    # Process and upload
    print("\nSession stats:")
    stats = handler.get_stats()
    for key, value in stats.items():
        print(f"  {key}: {value}")
        
    # Uncomment to actually process and upload:
    # result = await process_realtime_session(handler, upload_to_blob=True)
    # print(f"Result: {result}")


async def example_with_local_audio_files():
    """
    Example using local audio files for input and output
    """
    handler = RealtimeAudioHandler()
    
    # If you have recorded audio files (PCM16, 24kHz)
    # Uncomment and modify paths as needed:
    
    # with open("input_audio.pcm", "rb") as f:
    #     handler.add_input_audio(f.read())
    #     
    # with open("output_audio.pcm", "rb") as f:
    #     handler.add_output_audio(f.read())
    
    # Save as MP3
    try:
        mp3_path = handler.save_mp3_local("conversation.mp3")
        print(f"MP3 saved to: {mp3_path}")
        
        # Get stats
        stats = handler.get_stats()
        print(f"Total duration: {stats['total_duration_seconds']}s")
        
    except Exception as e:
        print(f"Error: {e}")


def example_integration_snippet():
    """
    Code snippet showing how to integrate with your existing realtime code
    """
    code = '''
# In your existing GPT Realtime API code:

from realtime_audio_handler import RealtimeAudioHandler, process_realtime_session

# Initialize at the start of your session
audio_handler = RealtimeAudioHandler(
    blob_connection_string="your_connection_string",
    blob_container="audio-recordings"
)

# When receiving input audio from user (if you're sending it to API):
# audio_handler.add_input_audio_base64(user_audio_base64)

# When receiving output audio from API:
async for message in websocket:
    event = json.loads(message)
    
    if event["type"] == "response.audio.delta":
        # Capture output audio
        audio_handler.add_output_audio_base64(event["delta"])
    
    elif event["type"] == "response.done":
        # Audio is complete, process and upload
        result = await process_realtime_session(audio_handler, upload_to_blob=True)
        print(f"Audio saved: {result}")
        
        # Start fresh for next conversation
        audio_handler.clear_audio()
'''
    print("Integration Example:")
    print(code)


if __name__ == "__main__":
    print("=== GPT Realtime Audio Handler Examples ===\n")
    
    # Show integration snippet
    example_integration_snippet()
    
    print("\n" + "="*50 + "\n")
    
    # Run async examples
    # asyncio.run(example_realtime_session())
    # asyncio.run(example_with_local_audio_files())
    
    print("To run examples, uncomment the desired example in the __main__ block")
