"""
GPT Realtime Audio Handler
Captures input and output audio from GPT Realtime API,
combines them into MP3, and uploads to blob storage.
"""

import asyncio
import base64
import json
import os
from datetime import datetime
from typing import Optional, List
import io

try:
    from pydub import AudioSegment
except ImportError:
    AudioSegment = None

try:
    from azure.storage.blob import BlobServiceClient, ContentSettings
except ImportError:
    BlobServiceClient = None


class RealtimeAudioHandler:
    """Handler for GPT Realtime API audio processing"""
    
    def __init__(self, blob_connection_string: Optional[str] = None, 
                 blob_container: str = "audio-recordings"):
        """
        Initialize the audio handler
        
        Args:
            blob_connection_string: Azure Blob Storage connection string
            blob_container: Name of the blob container
        """
        self.input_audio_chunks: List[bytes] = []
        self.output_audio_chunks: List[bytes] = []
        self.blob_connection_string = blob_connection_string or os.getenv('AZURE_STORAGE_CONNECTION_STRING')
        self.blob_container = blob_container
        self.session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        
    def add_input_audio(self, audio_data: bytes):
        """
        Add input audio chunk
        
        Args:
            audio_data: Raw audio bytes (PCM16, 24kHz)
        """
        self.input_audio_chunks.append(audio_data)
        
    def add_output_audio(self, audio_data: bytes):
        """
        Add output audio chunk
        
        Args:
            audio_data: Raw audio bytes (PCM16, 24kHz)
        """
        self.output_audio_chunks.append(audio_data)
        
    def add_input_audio_base64(self, audio_base64: str):
        """
        Add input audio chunk from base64 string
        
        Args:
            audio_base64: Base64 encoded audio data
        """
        audio_data = base64.b64decode(audio_base64)
        self.add_input_audio(audio_data)
        
    def add_output_audio_base64(self, audio_base64: str):
        """
        Add output audio chunk from base64 string
        
        Args:
            audio_base64: Base64 encoded audio data
        """
        audio_data = base64.b64decode(audio_base64)
        self.add_output_audio(audio_data)
        
    def _combine_audio_chunks(self, chunks: List[bytes]) -> bytes:
        """
        Combine multiple audio chunks into a single audio buffer
        
        Args:
            chunks: List of raw audio byte chunks
            
        Returns:
            Combined audio bytes
        """
        return b''.join(chunks)
        
    def synthesize_mp3(self, sample_rate: int = 24000, channels: int = 1) -> bytes:
        """
        Synthesize input and output audio into a single MP3 file
        
        Args:
            sample_rate: Audio sample rate (default: 24000 for GPT Realtime)
            channels: Number of audio channels (default: 1 for mono)
            
        Returns:
            MP3 audio bytes
        """
        if AudioSegment is None:
            raise ImportError("pydub is required for audio synthesis. Install with: pip install pydub")
            
        # Combine input audio chunks
        input_audio_raw = self._combine_audio_chunks(self.input_audio_chunks)
        
        # Combine output audio chunks
        output_audio_raw = self._combine_audio_chunks(self.output_audio_chunks)
        
        # Create AudioSegment objects from raw PCM16 data
        # GPT Realtime API uses PCM16 format at 24kHz
        input_segment = AudioSegment(
            data=input_audio_raw,
            sample_width=2,  # 16-bit = 2 bytes
            frame_rate=sample_rate,
            channels=channels
        ) if input_audio_raw else AudioSegment.silent(duration=0)
        
        output_segment = AudioSegment(
            data=output_audio_raw,
            sample_width=2,
            frame_rate=sample_rate,
            channels=channels
        ) if output_audio_raw else AudioSegment.silent(duration=0)
        
        # Combine audio: input followed by output
        # Add a small silence gap between them
        silence = AudioSegment.silent(duration=500)  # 500ms silence
        combined = input_segment + silence + output_segment
        
        # Export to MP3
        mp3_buffer = io.BytesIO()
        combined.export(mp3_buffer, format="mp3", bitrate="128k")
        mp3_buffer.seek(0)
        
        return mp3_buffer.read()
        
    def save_mp3_local(self, filename: Optional[str] = None) -> str:
        """
        Save the synthesized MP3 file locally
        
        Args:
            filename: Output filename (default: auto-generated)
            
        Returns:
            Path to saved file
        """
        if filename is None:
            filename = f"conversation_{self.session_id}.mp3"
            
        mp3_data = self.synthesize_mp3()
        
        with open(filename, 'wb') as f:
            f.write(mp3_data)
            
        return filename
        
    async def upload_to_blob(self, blob_name: Optional[str] = None) -> str:
        """
        Upload the synthesized MP3 to Azure Blob Storage
        
        Args:
            blob_name: Name for the blob (default: auto-generated)
            
        Returns:
            URL of the uploaded blob
        """
        if BlobServiceClient is None:
            raise ImportError("azure-storage-blob is required. Install with: pip install azure-storage-blob")
            
        if not self.blob_connection_string:
            raise ValueError("Azure Storage connection string not provided")
            
        if blob_name is None:
            blob_name = f"conversation_{self.session_id}.mp3"
            
        # Synthesize MP3
        mp3_data = self.synthesize_mp3()
        
        # Upload to blob storage
        blob_service_client = BlobServiceClient.from_connection_string(self.blob_connection_string)
        
        # Create container if it doesn't exist
        try:
            container_client = blob_service_client.get_container_client(self.blob_container)
            if not container_client.exists():
                container_client.create_container()
        except Exception as e:
            print(f"Container check/creation error: {e}")
            
        # Upload blob
        blob_client = blob_service_client.get_blob_client(
            container=self.blob_container,
            blob=blob_name
        )
        
        content_settings = ContentSettings(content_type='audio/mpeg')
        blob_client.upload_blob(
            mp3_data,
            overwrite=True,
            content_settings=content_settings
        )
        
        return blob_client.url
        
    def clear_audio(self):
        """Clear all stored audio chunks"""
        self.input_audio_chunks.clear()
        self.output_audio_chunks.clear()
        
    def get_stats(self) -> dict:
        """
        Get statistics about collected audio
        
        Returns:
            Dictionary with audio statistics
        """
        input_size = sum(len(chunk) for chunk in self.input_audio_chunks)
        output_size = sum(len(chunk) for chunk in self.output_audio_chunks)
        
        # Calculate duration (PCM16 at 24kHz, mono = 48000 bytes per second)
        bytes_per_second = 24000 * 2  # sample_rate * bytes_per_sample
        input_duration = input_size / bytes_per_second if input_size > 0 else 0
        output_duration = output_size / bytes_per_second if output_size > 0 else 0
        
        return {
            'session_id': self.session_id,
            'input_chunks': len(self.input_audio_chunks),
            'output_chunks': len(self.output_audio_chunks),
            'input_size_bytes': input_size,
            'output_size_bytes': output_size,
            'input_duration_seconds': round(input_duration, 2),
            'output_duration_seconds': round(output_duration, 2),
            'total_duration_seconds': round(input_duration + output_duration, 2)
        }


# Example usage and helper functions
async def process_realtime_session(handler: RealtimeAudioHandler, 
                                   upload_to_blob: bool = True) -> str:
    """
    Process a realtime session after audio collection is complete
    
    Args:
        handler: RealtimeAudioHandler instance with collected audio
        upload_to_blob: Whether to upload to blob storage (default: True)
        
    Returns:
        Path or URL of the saved audio
    """
    stats = handler.get_stats()
    print(f"Processing session {stats['session_id']}")
    print(f"Input: {stats['input_duration_seconds']}s, Output: {stats['output_duration_seconds']}s")
    
    if upload_to_blob:
        try:
            url = await handler.upload_to_blob()
            print(f"Uploaded to blob: {url}")
            return url
        except Exception as e:
            print(f"Failed to upload to blob: {e}")
            print("Saving locally instead...")
            
    # Fallback to local save
    filepath = handler.save_mp3_local()
    print(f"Saved locally: {filepath}")
    return filepath
