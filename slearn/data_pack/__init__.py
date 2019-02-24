from .datapack import DataPack
from slearn.classes import Incident, State

class IncidentPack(DataPack):
    def __init__(self, header, data, meta):
        DataPack.__init__(self, Incident, header, data, meta)

class StatePack(DataPack):
    def __init__(self, header, data, meta):
        DataPack.__init__(self, State, header, data, meta)
