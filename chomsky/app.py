from typing import Optional
import os
import datetime

from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
#from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from metamodel import crud, models, schemas
from metamodel.database import SessionLocal, engine

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

templates = Jinja2Templates(directory="templates")

origins = os.environ['ORIGIN_URL']

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


#app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/home", response_class=HTMLResponse)
def get_home_page(request: Request, botid: Optional[str] = None):
    #botid = "1"
    return templates.TemplateResponse("home.html", {"request": request, "botid": botid})

@app.get("/")
def read_root():
    return {"status": "online"}


@app.post("/bot/{bot_id}/", response_model=schemas.BotFlowDiagram)
def create_bot_flow_diagram(bot_id: str, bot_flow_diagram: schemas.BotFlowDiagramCreate, db: Session = Depends(get_db)):
    bot_conf = crud.create_bot_flow_diagram(db, bot_id, bot_flow_diagram)
    if bot_conf is None:
        raise HTTPException(status_code=404, detail="Failed to create bot")
    return bot_conf

#fetch_bot_configuratin_by_bot_id : check if any bot configured for bot id
#Response JSON schema 
@app.get("/bot/{bot_id}/latest", response_model=schemas.BotFlowDiagram)
def get_bot_configuration_by_bot_id(bot_id: str, db: Session = Depends(get_db)):
    bot_conf = crud.get_bot_flow_diagram_by_bot_id(db, bot_id)
    if bot_conf is None:
        raise HTTPException(status_code=404, detail="Bot not found")
    return bot_conf

@app.post("/bot/{bot_id}/{id}", response_model=schemas.BotFlowDiagram)
def provision_bot(bot_id: str, id: str, db: Session = Depends(get_db)):
    bot_conf = crud.provision_bot(db, bot_id, id)
    if bot_conf is None:
        raise HTTPException(status_code=404, detail="Bot not found")
    return bot_conf