import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

#Doc location : https://fastapi.tiangolo.com/tutorial/sql-databases/

#SQLALCHEMY_DATABASE_URL = "sqlite:///./sql_app.db"
SQLALCHEMY_DATABASE_URL = "postgresql://"+os.environ['DB_USERNAME']+":"+ os.environ['DB_PASSWORD']+ "@"+os.environ['DB_HOST']+":"+os.environ['DB_PORT']+"/"+os.environ['DB_DATABASE']
print("============DATA BASE URL =======================")
print(SQLALCHEMY_DATABASE_URL)
engine = create_engine(
    SQLALCHEMY_DATABASE_URL
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()