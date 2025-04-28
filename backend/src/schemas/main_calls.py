from pydantic import BaseModel
from datetime import datetime

class MainCall(BaseModel):
    request_id = int 
    type_request = str
    date = datetime
    phone = str
    comment_req = str
    service = str
    sources = str
    fio = str
    links = str
    class Config:
        json_encoders = {
            datetime: lambda v: v.strftime("%Y-%m-%d %H:%M:%S")
  # Сериализация в нужный формат
        }