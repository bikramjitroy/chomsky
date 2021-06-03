import uuid
from sqlalchemy.orm import Session

from . import models, schemas


from generate_rasa_config import bot_generation

#Schama is the JSON schema for REST api request
def create_bot_flow_diagram(db: Session, bot_id: str, schema: schemas.BotFlowDiagramCreate):

    id = str(uuid.uuid1())
    db_entry = models.BotFlowDiagram(id=id,
                    bot_id = bot_id,
                    bot_type=schema.bot_type,
                    bot_diagram=schema.bot_diagram,
                    bot_diagram_schema_version=schema.bot_diagram_schema_version,
                    description=schema.description)

    db.add(db_entry)
    db.commit()
    db.refresh(db_entry)
    return db_entry

def get_bot_flow_diagram_by_bot_id(db: Session, bot_id: str):
    return db.query(models.BotFlowDiagram).filter(models.BotFlowDiagram.bot_id == bot_id).first()



def provision_bot(db: Session, bot_id: str, id: str):
    response = db.query(models.BotFlowDiagram).filter(models.BotFlowDiagram.bot_id == bot_id and models.BotFlowDiagram.id == id).first()
    config_path = "/tmp/rasa_config/" + id + "/"
    #print("response", response.bot_diagram["graph"])
    bot_generation(response.bot_diagram["graph"], config_path)

    return response