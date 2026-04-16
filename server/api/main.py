from fastapi import FastAPI, HTTPException
from uuid import uuid4 as uuid
import InfluxManager


app = FastAPI()
db_manager = InfluxManager()

@app.get("/generate-uuid")
def get_uuid():
    """generates and returns a new uuid"""
    return {"uuid": str(uuid())}

@app.get("/data")
def get_data(sensor: str, start: int, end: int, uid: str):
    """get recorded data for a certain sensor and user in a given timespan"""
    try:
        data = db_manager.query_sensor(sensor, start, end, uid)
        return {"sensor": sensor, "count": len(data), "values": data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))