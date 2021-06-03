from typing import Optional
from enum import Enum
import datetime

from pydantic import BaseModel

class BotFlowDiagramBase(BaseModel):
    bot_type: str                         #ChatClick/ChatNLP/Voicebot
    bot_diagram_schema_version: str       #JSON Schema Version 
    description: Optional[str] = None
    bot_diagram: dict                     # Diagram JSON file

class BotFlowDiagram(BotFlowDiagramBase):
    id: str
    bot_id: str                           # for a single bot ID - multiple entry could be found
    creation_time: datetime.datetime

    class Config:
        orm_mode = True

class BotFlowDiagramCreate(BotFlowDiagramBase):
    pass