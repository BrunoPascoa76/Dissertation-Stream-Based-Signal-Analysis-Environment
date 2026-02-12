from unittest.mock import MagicMock
import pytest
from plugins.sensors.KeyboardReader import KeyboardReader
from pynput import keyboard

from utils.MQTTHelper import MQTTHelper

@pytest.fixture
def mock_listener():
    return MagicMock(spec=keyboard.Listener)

@pytest.fixture
def mock_publisher():
    return MagicMock(MQTTHelper)

@pytest.fixture
def reader(mock_listener, mock_publisher):
    """KeyboardReader instance with mocked listener and publisher"""
    return KeyboardReader(listener=mock_listener, publisher=mock_publisher)

def test_start_starts_listener(reader, mock_listener):
    reader.start()
    mock_listener.start.assert_called_once()
    assert reader._running is True

def test_stop_stops_listener(reader, mock_listener):
    reader._running = True
    reader._listener = mock_listener
    reader.stop()
    mock_listener.stop.assert_called_once()
    assert reader._running is False
    assert reader._listener is None
    
@pytest.mark.parametrize(
    "key,expected_category",
    [
        (keyboard.KeyCode.from_char("a"), "letter"),
        (keyboard.KeyCode.from_char("Z"), "letter"),
        (keyboard.KeyCode.from_char("5"), "digit"),
        (keyboard.Key.space, "whitespace"),
        (keyboard.Key.tab, "whitespace"),
        (keyboard.Key.backspace, "delete"),
        (keyboard.Key.delete, "delete"),
        (keyboard.Key.enter, "enter"),
        (keyboard.Key.f1, "special"),
        (keyboard.KeyCode.from_char("@"), "special"),
        (keyboard.KeyCode(char=None), "unknown")
    ]
)
def test_on_press_sends_correct_category(reader, mock_publisher, key, expected_category):
    reader._on_press(key)

    # Assert publisher.publish was called once
    mock_publisher.publish.assert_called_once()

    # Extract payload sent
    topic, payload = mock_publisher.publish.call_args[0]

    # Check topic
    assert topic == "sensors/keyboard"

    # Check category
    assert payload["category"] == expected_category

    # Check timestamp exists and is int
    assert isinstance(payload["timestamp"], int)
    assert payload["timestamp"] > 0

    # Reset for next iteration
    mock_publisher.publish.reset_mock()