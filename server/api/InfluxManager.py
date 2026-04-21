import os
from influxdb import InfluxDBClient

class InfluxManager:
    def __init__(self):
        self.host = "influxdb"
        self.port = int(os.getenv("INFLUXDB_PORT", 8086))
        self.db = os.getenv("INFLUXDB_DB", "mqtt")
        self.client = InfluxDBClient(host=self.host, port=self.port, database=self.db)

    def query(self,query):
        try:
            self.client.query(query)
        except Exception as e:
            raise(e)