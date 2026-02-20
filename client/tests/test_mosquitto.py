import time

from pluggy import PluginManager
from plugins.core.MosquittoLauncher import MosquittoManager
import pytest
from pathlib import Path

CONFIG_PATH = Path("conf/mosquitto.conf").resolve()


@pytest.fixture
def mosquitto_manager():
    """Fixture to create and clean up MosquittoManager."""
    manager = MosquittoManager(config_path=str(CONFIG_PATH))
    yield manager
    # Ensure cleanup after tests
    manager.stop()

def wait_for_container(container, timeout=30, interval=0.5):
    """Wait until the container is actually running."""
    start = time.time()
    while time.time() - start < timeout:
        container.reload()
        if container.status == "running" or container.attrs["State"]["Running"]:
            return
        time.sleep(interval)
    raise TimeoutError(f"Container {container.name} did not reach 'running' state in {timeout}s")

def ensure_running(manager):
    """Start the container if not running, and wait until ready."""
    if manager.container is None or manager.container.status != "running":
        manager.start(wait_for_ready=True)
    wait_for_container(manager.container)
    assert manager._port_open(), "Broker port should be open"


def test_start_broker(mosquitto_manager):
    """Test that the Mosquitto broker starts and is ready."""
    ensure_running(mosquitto_manager)


def test_container_running(mosquitto_manager):
    """Test that the container is running after start."""
    ensure_running(mosquitto_manager)
    container = mosquitto_manager.container
    assert container is not None
    assert container.status == "running"


def test_stop_broker(mosquitto_manager):
    """Test that the broker can be stopped."""
    ensure_running(mosquitto_manager)
    mosquitto_manager.stop()

    # Container should be gone or not running
    container = None
    try:
        container = mosquitto_manager.client.containers.get(
            mosquitto_manager.container_name
        )
    except:
        pass
    assert container is None or container.status != "running"