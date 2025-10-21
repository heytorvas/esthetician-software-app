import uuid
from datetime import datetime, date

def serialize_for_mongo(obj):
    """
    Recursively convert UUID and datetime/date objects to strings for MongoDB storage.
    """
    if isinstance(obj, dict):
        return {k: serialize_for_mongo(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [serialize_for_mongo(i) for i in obj]
    elif isinstance(obj, uuid.UUID):
        return str(obj)
    elif isinstance(obj, (datetime, date)):
        return obj.isoformat()
    else:
        return obj

def deserialize_from_mongo(obj):
    """
    Recursively convert string UUIDs and ISO datetimes back to Python objects if needed.
    (Optional: implement if you want to auto-convert on read)
    """
    # For now, just return as-is. Implement if needed.
    return obj
