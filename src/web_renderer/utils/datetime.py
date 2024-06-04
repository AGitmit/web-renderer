from typing import Annotated
from datetime import datetime


def get_timestamp() -> Annotated[float, "timestamp in epoch-time"]:
    time_now = datetime.now().strftime("%d.%m.%Y %H:%M:%S,%f")
    time_obj = datetime.strptime(time_now, "%d.%m.%Y %H:%M:%S,%f")
    timestamp = float(datetime.timestamp(time_obj))
    return timestamp
