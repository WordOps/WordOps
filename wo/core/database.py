"""WordOps generic database creation module"""
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import scoped_session, sessionmaker

from wo.core.variables import WOVar

# db_path = self.app.config.get('site', 'db_path')
engine = create_engine(WOVar.wo_db_uri, convert_unicode=True)
db_session = scoped_session(sessionmaker(autocommit=False,
                                         autoflush=False,
                                         bind=engine))
Base = declarative_base()
Base.query = db_session.query_property()


def init_db(app):
    """
    Initializes and creates all tables from models into the database
    """
    # import all modules here that might define models so that
    # they will be registered properly on the metadata.  Otherwise
    # # you will have to import them first before calling init_db()
    # import wo.core.models
    try:
        app.log.info("Initializing WordOps Database")
        Base.metadata.create_all(bind=engine)
    except Exception as e:
        app.log.debug("{0}".format(e))
