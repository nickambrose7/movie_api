import os
import dotenv
from sqlalchemy import create_engine
import sqlalchemy

# DO NOT CHANGE THIS TO BE HARDCODED. ONLY PULL FROM ENVIRONMENT VARIABLES.

def database_connection_url():
    dotenv.load_dotenv()
    DB_USER: str = os.environ.get("POSTGRES_USER")
    DB_PASSWD = os.environ.get("POSTGRES_PASSWORD")
    DB_SERVER: str = os.environ.get("POSTGRES_SERVER")
    DB_PORT: str = os.environ.get("POSTGRES_PORT")
    DB_NAME: str = os.environ.get("POSTGRES_DB")
    return f"postgresql://{DB_USER}:{DB_PASSWD}@{DB_SERVER}:{DB_PORT}/{DB_NAME}"

engine = create_engine(database_connection_url())

conn = engine.connect()

metadata_obj = sqlalchemy.MetaData()
movies = sqlalchemy.Table("Movies", metadata_obj, autoload_with=engine)
characters = sqlalchemy.Table("Characters", metadata_obj, autoload_with=engine)
conversations = sqlalchemy.Table("Conversations", metadata_obj, autoload_with=engine)
lines = sqlalchemy.Table("Lines", metadata_obj, autoload_with=engine)
