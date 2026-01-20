#!/usr/bin/env python3
"""
Demo script showing the complete workflow of the GPT Realtime Audio Handler
This demonstrates how to use the library with simulated audio data
"""

import asyncio
import os
import sys
from datetime import datetime
from realtime_audio_handler import RealtimeAudioHandler, process_realtime_session


def print_header(title):
    """Print a formatted header"""
    print("\n" + "="*60)
    print(f"  {title}")
    print("="*60 + "\n")


def simulate_audio_data(duration_seconds=2):
    """
    Simulate audio data (PCM16, 24kHz, mono)
    
    Args:
        duration_seconds: Duration of audio to generate
        
    Returns:
        bytes: Simulated PCM16 audio data
    """
    # PCM16 at 24kHz = 24000 samples/sec * 2 bytes/sample = 48000 bytes/sec
    bytes_per_second = 24000 * 2
    total_bytes = int(duration_seconds * bytes_per_second)
    
    # Generate silence (all zeros)
    return b'\x00\x00' * (total_bytes // 2)


async def demo_basic_usage():
    """Demo: Basic usage with local save"""
    print_header("Demo 1: Basic Usage - Save MP3 Locally")
    
    # Initialize handler
    handler = RealtimeAudioHandler()
    print("✓ Handler initialized")
    
    # Simulate receiving audio data
    print("\nSimulating audio capture...")
    print("  - Adding 2 seconds of input audio (user speaking)")
    input_audio = simulate_audio_data(duration_seconds=2)
    handler.add_input_audio(input_audio)
    
    print("  - Adding 3 seconds of output audio (AI response)")
    output_audio = simulate_audio_data(duration_seconds=3)
    handler.add_output_audio(output_audio)
    
    # Show statistics
    stats = handler.get_stats()
    print("\n📊 Audio Statistics:")
    print(f"  Session ID: {stats['session_id']}")
    print(f"  Input chunks: {stats['input_chunks']}")
    print(f"  Output chunks: {stats['output_chunks']}")
    print(f"  Input duration: {stats['input_duration_seconds']}s")
    print(f"  Output duration: {stats['output_duration_seconds']}s")
    print(f"  Total duration: {stats['total_duration_seconds']}s")
    
    # Save as MP3
    print("\n💾 Saving MP3 file...")
    filename = f"/tmp/demo_conversation_{handler.session_id}.mp3"
    saved_path = handler.save_mp3_local(filename)
    
    # Check file size
    file_size = os.path.getsize(saved_path)
    print(f"✓ Saved to: {saved_path}")
    print(f"  File size: {file_size:,} bytes")
    
    # Clean up
    print("\n🧹 Cleaning up demo file...")
    os.remove(saved_path)
    print("✓ Demo file removed")


async def demo_with_blob_upload():
    """Demo: Upload to blob storage (simulated)"""
    print_header("Demo 2: Blob Upload (Configuration Example)")
    
    # Check for Azure credentials
    connection_string = os.getenv('AZURE_STORAGE_CONNECTION_STRING')
    
    if not connection_string:
        print("ℹ️  No Azure Storage credentials found")
        print("\nTo enable blob upload, set the following environment variables:")
        print("  AZURE_STORAGE_CONNECTION_STRING=your_connection_string")
        print("\nExample usage:")
        print("""
    handler = RealtimeAudioHandler(
        blob_connection_string="your_connection_string",
        blob_container="audio-recordings"
    )
    
    # ... add audio chunks ...
    
    # Upload to blob
    url = await handler.upload_to_blob()
    print(f"Uploaded to: {url}")
        """)
    else:
        print("✓ Azure Storage credentials found")
        print("\nTo upload to blob storage:")
        
        # Show example with actual credentials
        handler = RealtimeAudioHandler(
            blob_connection_string=connection_string,
            blob_container="audio-recordings"
        )
        
        # Add sample audio
        handler.add_output_audio(simulate_audio_data(duration_seconds=1))
        
        print("\n⚠️  Actual upload disabled in demo mode")
        print("In production, use:")
        print("  url = await handler.upload_to_blob()")


def demo_integration_snippet():
    """Demo: Show integration code"""
    print_header("Demo 3: Integration with GPT Realtime API")
    
    print("Integration code snippet:")
    print("""
import json
import websockets
from realtime_audio_handler import RealtimeAudioHandler

async def realtime_conversation():
    # Initialize handler
    handler = RealtimeAudioHandler()
    
    # Connect to GPT Realtime API
    url = "wss://api.openai.com/v1/realtime?model=gpt-4o-realtime-preview-2024-12-17"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "OpenAI-Beta": "realtime=v1"
    }
    
    async with websockets.connect(url, extra_headers=headers) as websocket:
        # Configure session
        await websocket.send(json.dumps({
            "type": "session.update",
            "session": {
                "modalities": ["audio"],
                "input_audio_format": "pcm16",
                "output_audio_format": "pcm16"
            }
        }))
        
        # Handle messages
        async for message in websocket:
            event = json.loads(message)
            
            # Capture output audio
            if event["type"] == "response.audio.delta":
                handler.add_output_audio_base64(event["delta"])
            
            # When conversation is done
            elif event["type"] == "response.done":
                # Save audio
                handler.save_mp3_local("conversation.mp3")
                print("Audio saved!")
                
                # Start fresh for next conversation
                handler.clear_audio()
    """)


def demo_features():
    """Demo: Show all features"""
    print_header("Demo 4: Feature Overview")
    
    features = [
        ("🎤 Input Audio Capture", "Capture user's voice input"),
        ("🔊 Output Audio Capture", "Capture AI's voice response"),
        ("🎵 MP3 Synthesis", "Combine input + output into single MP3"),
        ("☁️ Blob Upload", "Upload to Azure Blob Storage"),
        ("📊 Statistics", "Track duration, size, chunk count"),
        ("🔄 Session Management", "Clear and reset for new conversations"),
        ("⚙️ Configurable", "Customize sample rate, bitrate, etc."),
        ("✅ Tested", "Full test suite included"),
    ]
    
    print("Features of GPT Realtime Audio Handler:\n")
    for emoji_feature, description in features:
        print(f"  {emoji_feature}")
        print(f"    {description}\n")


async def main():
    """Run all demos"""
    print("\n" + "🎵" * 30)
    print("  GPT REALTIME AUDIO HANDLER - DEMO")
    print("🎵" * 30)
    
    # Demo 1: Basic usage
    await demo_basic_usage()
    
    # Demo 2: Blob upload
    await demo_with_blob_upload()
    
    # Demo 3: Integration
    demo_integration_snippet()
    
    # Demo 4: Features
    demo_features()
    
    # Final notes
    print_header("Next Steps")
    print("📖 Read QUICKSTART.md for installation and usage guide")
    print("📚 See README.md for complete API documentation")
    print("🧪 Run test_handler.py to verify your setup")
    print("💡 Check example_usage.py for more examples")
    print("\nHappy coding! 🚀\n")


if __name__ == "__main__":
    asyncio.run(main())
