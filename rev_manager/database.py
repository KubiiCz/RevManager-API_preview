from sqlalchemy import create_engine, MetaData
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session

from rev_manager.config import Config


engine = create_engine(
    Config.SQLALCHEMY_DATABASE_URI + '?charset=utf8',
    convert_unicode=True, pool_pre_ping=True, pool_size=15, max_overflow=0, echo=False)

db_session = scoped_session(sessionmaker(autocommit=False,
                                         autoflush=False,
                                         bind=engine))
mymetadata = MetaData()
Base = declarative_base(metadata=mymetadata)

def init_db():
    import rev_manager.models.models
    # import all modules here that might define models so that
    # they will be registered properly on the metadata.  Otherwise
    # you will have to import them first before calling init_db()
    # Base.metadata.drop_all(engine)
    # Base.metadata.create_all(engine)


