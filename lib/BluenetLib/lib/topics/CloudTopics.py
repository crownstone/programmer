from enum import Enum

class CloudTopics(Enum):
    
    personEnteredLocation = "personEnteredLocation" # data is dictionary: {"locationId": str, "name": str, "person": {"id": str, "email": str, "name": str}}
    personLeftLocation = "personLeftLocation" # data is dictionary: {"locationId": str, "name": str, "person": {"id": str, "email": str, "name": str}}

