import re
from typing import Optional

from fastapi import FastAPI, HTTPException
from uuid import uuid4 as uuid
import InfluxManager


app = FastAPI()
db_manager = InfluxManager()

@app.get("/generate-uuid")
def get_uuid():
    """generates and returns a new uuid"""
    return {"uuid": str(uuid())}

@app.get("/data/{sensor}")
def get_flexible_data(sensor: str, start: int, end: int, uuid: str, agg: str = "AVG", field: str = "value",interval: Optional[str] = None):
    """query the database using pre-approved parameters"""
    allowed_aggs = ["AVG", "COUNT", "SUM", "MIN", "MAX", "LAST"] #whitelisted aggregators
    if agg.upper() not in allowed_aggs:
        raise HTTPException(status_code=400, detail="Invalid aggregation")
    
    safe_agg = agg.upper()
    safe_field = field.replace('"', '') #sanitize the field
    
    query= (
        f'SELECT {safe_agg}("{safe_field}") FROM "{sensor}" '
        f"WHERE \"uuid\" = '{uuid}' "
        f"AND time >= {start}ms AND time <= {end}ms"
    )
    
    #allow to group per interval (for example for keys-per-minute)
    if interval:
        if not re.match(r"^\d+(ms|[smhd])$", interval):
            raise HTTPException(status_code=400, detail="Invalid interval format (use 1s, 1m, etc.)")
        query += f" GROUP BY time({interval}) fill(0)"
    try:    
        result = db_manager.query(query)
        return {"results": list(result.get_points())}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))