#!/usr/bin/env python3
"""
Test script to verify all components are working correctly.
Run: python test_components.py
"""

import os
import sys
import logging
from pathlib import Path
from dotenv import load_dotenv

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

load_dotenv()


def test_env_variables():
    """Test if all required environment variables are set."""
    logger.info("Testing environment variables...")
    
    required_vars = [
        "TELEGRAM_TOKEN",
        "OPENAI_API_KEY",
        "REPLICATE_API_TOKEN",
        "CHAT_ID"
    ]
    
    missing = []
    for var in required_vars:
        if not os.getenv(var):
            missing.append(var)
            logger.error(f"  ❌ {var} not set")
        else:
            logger.info(f"  ✓ {var} found")
    
    return len(missing) == 0


def test_imports():
    """Test if all required packages can be imported."""
    logger.info("Testing imports...")
    
    packages = [
        ("telegram", "python-telegram-bot"),
        ("openai", "openai"),
        ("replicate", "replicate"),
        ("dotenv", "python-dotenv"),
        ("serial", "pyserial"),
    ]
    
    failed = []
    for package, name in packages:
        try:
            __import__(package)
            logger.info(f"  ✓ {name}")
        except ImportError:
            failed.append(name)
            logger.error(f"  ❌ {name} - run: pip install {name}")
    
    return len(failed) == 0


def test_custom_modules():
    """Test if all custom modules can be imported."""
    logger.info("Testing custom modules...")
    
    modules = [
        "archiver",
        "sensor_controller",
        "image_analyzer",
        "serial_handler",
        "audio_handler",
        "bot",
    ]
    
    failed = []
    for module in modules:
        try:
            __import__(module)
            logger.info(f"  ✓ {module}")
        except Exception as e:
            failed.append((module, str(e)))
            logger.error(f"  ❌ {module} - {e}")
    
    return len(failed) == 0


def test_directories():
    """Test if required directories can be created."""
    logger.info("Testing directory creation...")
    
    dirs = ["photos", "photos/archive", "audio", "audio/archive"]
    
    for dir_path in dirs:
        try:
            Path(dir_path).mkdir(parents=True, exist_ok=True)
            logger.info(f"  ✓ {dir_path}")
        except Exception as e:
            logger.error(f"  ❌ {dir_path} - {e}")
            return False
    
    return True


def test_sensor_controller():
    """Test sensor controller in simulation mode."""
    logger.info("Testing SensorController (simulation mode)...")
    
    try:
        from sensor_controller import SensorController
        sensor = SensorController()
        
        # Test distance measurement
        dist = sensor.measure_distance()
        logger.info(f"  ✓ Distance measurement: {dist} cm")
        
        # Test LED color (won't actually light up in simulation)
        sensor.set_color(1, 0, 0)
        logger.info(f"  ✓ LED color setting")
        
        sensor.cleanup()
        return True
    except Exception as e:
        logger.error(f"  ❌ {e}")
        return False


def test_image_analyzer():
    """Test that image analyzer can be instantiated."""
    logger.info("Testing ImageAnalyzer...")
    
    try:
        from image_analyzer import ImageAnalyzer
        analyzer = ImageAnalyzer()
        logger.info(f"  ✓ ImageAnalyzer initialized")
        logger.info(f"  ✓ Available moods: happy, flirty, angry, bored")
        return True
    except Exception as e:
        logger.error(f"  ❌ {e}")
        return False


def test_audio_handler():
    """Test that audio handler can be instantiated."""
    logger.info("Testing AudioHandler...")
    
    try:
        from audio_handler import AudioHandler
        handler = AudioHandler()
        logger.info(f"  ✓ AudioHandler initialized")
        logger.info(f"  ✓ Available voices for moods")
        return True
    except Exception as e:
        logger.error(f"  ❌ {e}")
        return False


def test_serial_handler():
    """Test that serial handler can be instantiated."""
    logger.info("Testing SerialHandler...")
    
    try:
        from serial_handler import SerialHandler
        handler = SerialHandler()
        logger.info(f"  ✓ SerialHandler initialized (simulation mode)")
        handler.send_mood("happy")
        logger.info(f"  ✓ Mood sending works")
        handler.close()
        return True
    except Exception as e:
        logger.error(f"  ❌ {e}")
        return False


def main():
    """Run all tests."""
    logger.info("=" * 60)
    logger.info("ANDI System - Component Test Suite")
    logger.info("=" * 60)
    
    tests = [
        ("Environment Variables", test_env_variables),
        ("Package Imports", test_imports),
        ("Custom Modules", test_custom_modules),
        ("Directories", test_directories),
        ("SensorController", test_sensor_controller),
        ("ImageAnalyzer", test_image_analyzer),
        ("AudioHandler", test_audio_handler),
        ("SerialHandler", test_serial_handler),
    ]
    
    results = []
    for test_name, test_func in tests:
        logger.info("")
        try:
            passed = test_func()
            results.append((test_name, passed))
        except Exception as e:
            logger.error(f"Test failed with exception: {e}")
            results.append((test_name, False))
    
    # Summary
    logger.info("")
    logger.info("=" * 60)
    logger.info("TEST SUMMARY")
    logger.info("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✓ PASS" if result else "❌ FAIL"
        logger.info(f"{status}: {test_name}")
    
    logger.info(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        logger.info("\n🎉 All tests passed! System is ready to run.")
        logger.info("Start the system with: python main.py")
        return 0
    else:
        logger.error(f"\n⚠️  {total - passed} test(s) failed. Please fix the issues above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
