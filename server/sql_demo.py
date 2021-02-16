from sqlalchemy import *
from sqlalchemy.orm import mapper, sessionmaker
import sys,os
import uuid

sys.path[0]=os.path.dirname(os.path.realpath(__file__))

if __name__ == '__main__':
    import sys
    sys.path.append(os.getcwd())

from db_models import VggFeaturesVector
from db_manager import Session, engine, Base


Base.metadata.create_all(engine)

session = Session()

# Creating new object
obj = VggFeaturesVector()
session.add(obj)
session.commit()
obj_id = obj.id

# Retrieving existing object
obj = session.query(VggFeaturesVector).get(obj_id)
print(obj.id)
print(obj.features_vector)
import torch
obj.features_vector = torch.empty([25088])
print(obj.features_vector)
session.commit()
print(obj)