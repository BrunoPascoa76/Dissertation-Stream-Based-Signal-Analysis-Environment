import importlib.util
import pathlib

from utils.PluginManager import PluginManager


def test_core_plugins_load_and_start():
    manager = PluginManager()
    
    core_names=manager.list_core_plugins()
    
    assert any("MosquittoManager" in name for name in core_names), \
        "MosquittoManager should be discovered in core plugins"
        
    manager.start_core_plugins()

    mosquitto_instances = [p for p in manager.core_plugins if p.__class__.__name__ == "MosquittoManager"]
    assert mosquitto_instances, "MosquittoManager instance should exist"
    for instance in mosquitto_instances:
        status = instance.status()
        assert status in ("running", "created", "restarting"), f"Unexpected status: {status}"

    manager.stop_core_plugins()

    for instance in mosquitto_instances:
        assert instance.status() == "stopped"