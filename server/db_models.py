import torch
from datetime import datetime
import pickle
from sqlalchemy import Column, String, Integer, DateTime, BLOB
from db_manager import Base
from utils.utils import stringify_uuid4

class VggFeaturesVector(Base):

    __tablename__ = 'VggFeaturesVector'

    id = Column(String(36), primary_key=True, default=stringify_uuid4)
    data = Column(BLOB, nullable=False)
    label = Column(Integer, nullable=False)
    timestamp = Column(DateTime, nullable=False)

    def __init__(self, data=pickle.dumps(torch.zeros([25088])), label=0, timestamp=datetime.now()):
        self.data = data
        self.label = label
        self.timestamp = timestamp

    @property
    def features_vector(self):
        return pickle.loads(self.data)
    
    @features_vector.setter
    def features_vector(self, features_vector):
        self.data = pickle.dumps(features_vector)

    def __repr__(self):
        return f'Id:\t{self.id}\nFeatures vector:\t{self.features_vector.shape}\nLabel:\t{self.label}\nTimestamp:\t{self.timestamp.strftime("%Y-%m-%d %H:%M:%S")}'
