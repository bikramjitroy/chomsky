from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, DateTime, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from .database import Base


"""
This contains database entity for writing to database
The format is used for sqlalchemy
"""

class BotFlowDiagram(Base):
    __tablename__ = "bot_flow_diagram"

    id = Column('id',String, primary_key=True, index=True)
    bot_id = Column('bot_id',String)
    bot_type = Column('bot_type',String)
    bot_diagram = Column('bot_diagram',JSON)
    bot_diagram_schema_version = Column('bot_diagram_schema_version',String)
    description = Column('description',String)
    creation_time = Column('creation_time', DateTime(timezone=True), default=func.now())