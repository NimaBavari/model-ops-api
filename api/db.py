from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

from .models import Base
from .settings import DevelopmentConfig

engine = create_engine(DevelopmentConfig.DATABASE_URI)
Base.metadata.create_all(engine)
Session = scoped_session(sessionmaker(bind=engine, isolation_level="REPEATABLE READ"))
sess = Session()
