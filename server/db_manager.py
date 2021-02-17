from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os, sys

if __name__ == '__main__':
    sys.path.append(os.getcwd())
sys.path[0]=os.path.dirname(os.path.realpath(__file__))

from utils.configurator import Configurator

configurator = Configurator()

engine = create_engine(configurator.get('Database', 'connection_string'))
Session = sessionmaker(bind=engine)

Base = declarative_base()
