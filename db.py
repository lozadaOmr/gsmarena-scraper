from sqlalchemy import create_engine, Column, Integer, String, Text, and_
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base


class DbEngine(object):
    def __init__(self, args):
        self.engine_url = "%s://%s:%s@%s:%s/%s" % (
            args.scheme,
            args.username,
            args.password,
            args.host,
            args.port,
            args.database
        )

        self.create()

    def create(self):
        # create engine
        self.engine = create_engine(self.engine_url)

        # create session
        Session = sessionmaker(bind=self.engine)
        self.session = Session()


Base = declarative_base()


class Device(Base):
    __tablename__ = 'device'

    id = Column(Integer, primary_key=True, autoincrement=True)
    tac = Column(String(255))
    manufacturer = Column(String(255))
    model = Column(String(255))
    meta = Column(Text)
    url = Column(String(255))
