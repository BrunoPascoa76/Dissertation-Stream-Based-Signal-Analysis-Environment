import logging
from pathlib import Path
import socket
import time
import docker
from docker.errors import NotFound, DockerException, APIError

from utils.setupLogger import setup_logger


class MosquittoManager:
    """
    Uses Docker to manage a local instance of Mosquitto MQTT.
    """
    
    def __init__(self, config_path:str="./mosquitto.conf",container_name:str="mosquitto-broker",port:int=1883,image="eclipse-mosquitto:latest"):
        """
        :param config_path: Path to mosquitto.conf
        :type config_path: str
        :param container_name: Name of the docker container
        :type container_name: str
        :param port: Local port to expose
        :type port: int
        :param image: Docker image to use
        """
        
        self.config_path=str(Path(config_path).resolve())
        print(self.config_path)
        self.container_name=container_name
        self.port=port
        self.image=image
        self.logger=setup_logger(name="MosquittoManager",level=logging.DEBUG)
        
        try:
            self.client=docker.from_env()
            self.logger.debug("Docker client successfully started")
        except DockerException as e:
            self.logger.error("Docker not available")
            raise RuntimeError("Docker not available") from e
        self.container=None
        
    def start(self,wait_for_ready=True,timeout=10)->None:
        """
        start the mosquitto container
                
        :param wait_for_ready: Whether to wait until the container is ready to accept messages before returning
        :param timeout: Timeout for the container to start
        """
        self.logger.info(f"Starting Mosquitto container '{self.container_name}'...")
        
        try:
            image = self.client.images.pull("eclipse-mosquitto:latest")
            self.logger.debug(f"Pulled image {image.tags}")
        except docker.errors.APIError as e:
            self.logger.error(f"Failed to pull image: {e}")
        
        try: #try to start an existing container
            self.container=self.client.containers.get(self.container_name)
            self.logger.debug(f"Found existing container '{self.container_name}' with status {self.container.status}")
            if self.container.status!="running":
                self.container.start()
                self.logger.info(f"Container '{self.container_name}' resumed")
                
        except NotFound: #container does not exist yet, start the container
            self.logger.debug("No existing container found. Creating a new one.")
            self.container = self.client.containers.run(
                image=self.image,
                name=self.container_name,
                detach=True,
                ports={f"{self.port}/tcp": self.port},
                volumes={
                    self.config_path: {
                        "bind": "/mosquitto/config/mosquitto.conf",
                        "mode": "ro,Z",
                    }
                },
                restart_policy={"Name": "unless-stopped"},
            )
            self.logger.info(f"Container '{self.container_name}' created and started")
            
        if wait_for_ready:
            self._wait_for_broker(timeout=timeout)
        self.logger.info(f"Mosquitto container '{self.container_name}' is ready on port {self.port}")
        
    def stop(self)->None:
        """
        Stop the container (does nothing if it does not exist or is already stopped)
        """
        
        if self.container is None:
            try:
                self.container = self.client.containers.get(self.container_name)
            except NotFound:
                self.logger.warning("Container not found. Nothing to stop.")
                return
            
        try:
            self.container.stop()
            self.container.remove()
            self.logger.info(f"Mosquitto container '{self.container_name}' stopped and removed.")
            self.container = None
        except APIError as e:
            self.logger.error(f"Error stopping container: {e}")
            
    def _wait_for_broker(self, timeout: int = 10) -> None:
        """Wait until the broker port is open."""
        
        self.logger.debug(f"Waiting for broker to become ready on port {self.port}...")
        start = time.time()
        
        while time.time() - start < timeout:
            if self._port_open():
                self.logger.debug("Broker port is open")
                return
            time.sleep(0.5)
            
        self.logger.error("Mosquitto broker did not become available within timeout")
        raise RuntimeError("Mosquitto broker did not become available within timeout")

    def _port_open(self) -> bool:
        """Check if the MQTT port is open."""
        try:
            with socket.create_connection(("localhost", self.port), timeout=1):
                return True
        except OSError:
            return False
        