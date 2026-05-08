import re
from typing import Optional

from fastapi import FastAPI, HTTPException
from uuid import uuid4 as uuid
from InfluxManager import InfluxManager


app = FastAPI()
db_manager = InfluxManager()

@app.get("/generate-uuid")
def get_uuid():
    """generates and returns a new uuid"""
    return {"uuid": str(uuid())}

@app.get("/data/{sensor}")
def get_flexible_data(sensor: str, start: int, end: int, uuid: str, agg: str = "NONE", field: str = "value",interval: Optional[str] = None):
    """query the database using pre-approved parameters"""
    allowed_aggs = ["MEAN", "COUNT", "SUM", "MIN", "MAX", "LAST","NONE"] #whitelisted aggregators
    if agg.upper() not in allowed_aggs:
        raise HTTPException(status_code=400, detail="Invalid aggregation")
    
    safe_agg = agg.upper()
    fields_list = [f.strip() for f in field.replace('"', '').split(',')]
    print(fields_list)
    
    if safe_agg == "NONE":
        safe_fields = ", ".join([f'"{f}"' for f in fields_list])
        query = f'SELECT {safe_fields} FROM "sensors/{sensor}" '
    else:
        agg_fields = ", ".join([f'{safe_agg}("{f}")' for f in fields_list])
        query = f'SELECT {agg_fields} FROM "sensors/{sensor}" '
    
    query+= (
        f"WHERE \"uuid\" = '{uuid}' "
        f"AND time >= {start}ms AND time <= {end}ms"
    )
    print(query)
    
    #allow to group per interval (for example for keys-per-minute)
    if interval:
        if not re.match(r"^\d+(ms|[smhd])$", interval):
            raise HTTPException(status_code=400, detail="Invalid interval format (use 1s, 1m, etc.)")
        query += f" GROUP BY time({interval}) fill(0)"
    try:    
        result = db_manager.query(query)
        if result is None:
            print(f"Query returned None. Check InfluxDB connection or Database name.")
        else:
            return {"results": list(result.get_points())}
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail=str(e))