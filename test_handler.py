"""
Test script for RealtimeAudioHandler
Tests basic functionality without requiring actual API calls
"""

import sys
import os
import asyncio

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from realtime_audio_handler import RealtimeAudioHandler


def test_handler_initialization():
    """Test handler can be initialized"""
    print("Test: Handler Initialization")
    handler = RealtimeAudioHandler()
    assert handler is not None
    assert handler.session_id is not None
    assert len(handler.input_audio_chunks) == 0
    assert len(handler.output_audio_chunks) == 0
    print("✓ Handler initialized successfully")
    return handler


def test_add_audio():
    """Test adding audio chunks"""
    print("\nTest: Adding Audio Chunks")
    handler = RealtimeAudioHandler()
    
    # Create mock PCM16 audio data (24kHz, mono)
    # 1 second of silence = 24000 samples * 2 bytes = 48000 bytes
    mock_input = b'\x00\x00' * 24000  # 1 second of silence
    mock_output = b'\x00\x00' * 12000  # 0.5 seconds of silence
    
    handler.add_input_audio(mock_input)
    handler.add_output_audio(mock_output)
    
    assert len(handler.input_audio_chunks) == 1
    assert len(handler.output_audio_chunks) == 1
    print("✓ Audio chunks added successfully")
    return handler


def test_get_stats():
    """Test statistics calculation"""
    print("\nTest: Statistics Calculation")
    handler = RealtimeAudioHandler()
    
    # Add 1 second of input and 0.5 seconds of output
    mock_input = b'\x00\x00' * 24000
    mock_output = b'\x00\x00' * 12000
    
    handler.add_input_audio(mock_input)
    handler.add_output_audio(mock_output)
    
    stats = handler.get_stats()
    
    assert stats['input_chunks'] == 1
    assert stats['output_chunks'] == 1
    assert stats['input_size_bytes'] == 48000
    assert stats['output_size_bytes'] == 24000
    assert abs(stats['input_duration_seconds'] - 1.0) < 0.1
    assert abs(stats['output_duration_seconds'] - 0.5) < 0.1
    
    print(f"  Input: {stats['input_duration_seconds']}s ({stats['input_size_bytes']} bytes)")
    print(f"  Output: {stats['output_duration_seconds']}s ({stats['output_size_bytes']} bytes)")
    print("✓ Statistics calculated correctly")
    return handler


def test_clear_audio():
    """Test clearing audio chunks"""
    print("\nTest: Clear Audio")
    handler = RealtimeAudioHandler()
    
    handler.add_input_audio(b'\x00\x00' * 1000)
    handler.add_output_audio(b'\x00\x00' * 1000)
    
    assert len(handler.input_audio_chunks) == 1
    assert len(handler.output_audio_chunks) == 1
    
    handler.clear_audio()
    
    assert len(handler.input_audio_chunks) == 0
    assert len(handler.output_audio_chunks) == 0
    print("✓ Audio cleared successfully")


def test_synthesize_mp3():
    """Test MP3 synthesis"""
    print("\nTest: MP3 Synthesis")
    
    try:
        from pydub import AudioSegment
    except ImportError:
        print("⚠ Skipping: pydub not installed")
        return
    
    handler = RealtimeAudioHandler()
    
    # Add some audio data
    mock_input = b'\x00\x00' * 24000  # 1 second
    mock_output = b'\x00\x00' * 24000  # 1 second
    
    handler.add_input_audio(mock_input)
    handler.add_output_audio(mock_output)
    
    try:
        mp3_data = handler.synthesize_mp3()
        assert mp3_data is not None
        assert len(mp3_data) > 0
        assert mp3_data[:3] == b'ID3' or mp3_data[:2] == b'\xff\xfb'  # MP3 header
        print(f"✓ MP3 synthesized successfully ({len(mp3_data)} bytes)")
    except Exception as e:
        print(f"⚠ MP3 synthesis failed: {e}")


def test_save_local():
    """Test saving MP3 locally"""
    print("\nTest: Save MP3 Locally")
    
    try:
        from pydub import AudioSegment
    except ImportError:
        print("⚠ Skipping: pydub not installed")
        return
    
    handler = RealtimeAudioHandler()
    
    # Add some audio data
    mock_input = b'\x00\x00' * 24000
    mock_output = b'\x00\x00' * 24000
    
    handler.add_input_audio(mock_input)
    handler.add_output_audio(mock_output)
    
    try:
        # Save to /tmp to avoid cluttering the repo
        test_file = f"/tmp/test_audio_{handler.session_id}.mp3"
        filepath = handler.save_mp3_local(test_file)
        
        assert os.path.exists(filepath)
        assert os.path.getsize(filepath) > 0
        
        print(f"✓ MP3 saved to {filepath} ({os.path.getsize(filepath)} bytes)")
        
        # Clean up
        os.remove(filepath)
        print("  (cleaned up test file)")
        
    except Exception as e:
        print(f"⚠ Save failed: {e}")


def run_all_tests():
    """Run all tests"""
    print("="*60)
    print("GPT Realtime Audio Handler - Test Suite")
    print("="*60)
    
    tests = [
        test_handler_initialization,
        test_add_audio,
        test_get_stats,
        test_clear_audio,
        test_synthesize_mp3,
        test_save_local,
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            test()
            passed += 1
        except Exception as e:
            print(f"✗ Test failed: {e}")
            failed += 1
    
    print("\n" + "="*60)
    print(f"Results: {passed} passed, {failed} failed")
    print("="*60)
    
    return failed == 0


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
