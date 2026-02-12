import json
from unittest.mock import MagicMock
import pytest
import paho.mqtt.client as mqtt

from utils.MQTTHelper import MQTTHelper


@pytest.fixture
def mock_client():
    return MagicMock(spec=mqtt.Client)

@pytest.fixture
def mqtt_helper(mock_client):
    helper=MQTTHelper(client=mock_client)
    return helper

def test_connect_success(mqtt_helper, mock_client):
    mock_client.connect.side_effect = lambda *a, **k: mqtt_helper._on_connect(mock_client, None, None, 0)

    mqtt_helper.connect()

    mock_client.connect.assert_called_once_with("localhost", 1883, 60)
    mock_client.loop_start.assert_called_once()
    assert mqtt_helper._connected is True

def test_connect_failure_raises(mqtt_helper, mock_client):
    mock_client.connect.side_effect = lambda *a, **k: None  # does nothing

    import time
    original_sleep = time.sleep
    time.sleep = lambda x: None  # speed up the test loop
    try:
        with pytest.raises(ConnectionError):
            mqtt_helper.connect()
    finally:
        time.sleep = original_sleep

def test_disconnect_when_connected(mqtt_helper, mock_client):
    mqtt_helper._connected = True
    mqtt_helper.disconnect()

    mock_client.loop_stop.assert_called_once()
    mock_client.disconnect.assert_called_once()

def test_disconnect_when_not_connected(mqtt_helper, mock_client):
    mqtt_helper._connected = False
    mqtt_helper.disconnect()

    mock_client.loop_stop.assert_not_called()
    mock_client.disconnect.assert_not_called()

def test_publish_success(mqtt_helper, mock_client):
    mqtt_helper._connected = True
    mock_result = MagicMock(rc=mqtt.MQTT_ERR_SUCCESS)
    mock_client.publish.return_value = mock_result

    payload = {"foo": "bar"}
    mqtt_helper.publish("test/topic", payload, qos=1, retain=True)

    mock_client.publish.assert_called_once_with(
        "test/topic",
        json.dumps(payload),
        qos=1,
        retain=True
    )

def test_publish_when_disconnected_raises(mqtt_helper, mock_client):
    mqtt_helper._connected = False
    with pytest.raises(RuntimeError):
        mqtt_helper.publish("test/topic", {"foo": "bar"})