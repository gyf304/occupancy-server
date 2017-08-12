from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from . import config, model

engine = create_engine(config.DB_URI, echo=False)
session_factory = sessionmaker()
session_factory.configure(bind=engine)
model.Base.metadata.create_all(bind=engine)
