import os
from influxdb import InfluxDBClient

class InfluxManager:
    def __init__(self):
        self.host = "influxdb"
        self.port = int(os.getenv("INFLUXDB_PORT", 8086))
        self.db = os.getenv("INFLUXDB_DB", "mqtt")
        self.client = InfluxDBClient(host=self.host, port=self.port, database=self.db)

    def query_sensor(self, sensor_name, start_ms, end_ms, target_uuid):
        # InfluxQL for 1.8 using ms precision
        query = (
            f'SELECT * FROM "{sensor_name}" '
            f'WHERE "uuid" = \'{target_uuid}\' '
            f'AND time >= {start_ms}ms AND time <= {end_ms}ms'
        )
        result = self.client.query(query)
        return list(result.get_points())