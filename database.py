from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker , declarative_base
from sqlalchemy.exc import SQLAlchemyError

from dotenv import load_dotenv
import os

load_dotenv()

DB_USER = os.getenv("DB_USER")
DB_PASS = os.getenv("DB_PASS")
DB_HOST = os.getenv("DB_HOST")
DB_NAME = os.getenv("DB_NAME")

SQL_URL = f"mysql+pymysql://{DB_USER}:{DB_PASS}@{DB_HOST}/{DB_NAME}"          # mysql+pymysql://<username>:<password>@<host>/<database_name>  # @ => encoded => %40

engine = create_engine(SQL_URL)                                         # start the db connection
SessionLocal = sessionmaker(bind=engine)                                # we use it for queries ( bulding sessions )
Base = declarative_base()                                               # base class for defining ORM        

