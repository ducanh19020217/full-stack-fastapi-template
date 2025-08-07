# Generic message
from app.models import SQLModel
class Message(SQLModel):
    message: str