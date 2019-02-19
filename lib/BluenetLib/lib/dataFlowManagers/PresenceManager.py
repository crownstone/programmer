from BluenetLib._EventBusInstance import BluenetEventBus
from BluenetLib.lib.topics.SystemCloudTopics import SystemCloudTopics
from BluenetLib.lib.topics.CloudTopics import CloudTopics


class PresenceManager:
    
    def __init__(self):
        self.presence = {}
        BluenetEventBus.subscribe(SystemCloudTopics.presenceInLocationDownloadedFromCloud, self.handlePresenceInLocationFromCloud)
        
        
    def handlePresenceInLocationFromCloud(self, locationData):
        locationId = locationData["id"]
        
        # if we initialize, we do not send change events.
        initializing = False
        if locationId not in self.presence:
            self.presence[locationId] = {}
            initializing = True
            
        # construct dict to quickly match people that are in the location now that were not there before
        peopleInLocationDict = {}
        
        # make sure all people who are now in the location are in our presence list
        for person in locationData["presentPeople"]:
            peopleInLocationDict[person["id"]] = person
            if person["id"] not in self.presence[locationId]:
                # person is in the room now, was not before
                self.presence[locationId][person["id"]] = person
                
                # we do not want to send change events triggered by initialization
                if not initializing:
                    
                    self.newPersonInLocation(person, {"id": locationId, "name": locationData["name"], "cloudId": locationData["cloudId"]})
                else:
                    print("Skipping presence due to init")


        # check if there are people in the known list that are not in the new list
        peopleToDelete = []
        for personId in self.presence[locationData["id"]]:
            if personId not in peopleInLocationDict:
                # this person left the room, trigger change event.
                self.personLeftLocation(self.presence[locationData["id"]][personId], {"id": locationId, "name": locationData["name"]})
                peopleToDelete.append(personId)
                
                
        # finally delete all the people that are no longer in this room
        for personId in peopleToDelete:
            del self.presence[locationData["id"]][personId]
            
    def getPeopleInLocation(self,locationId):
        people = []
        
        if locationId in self.presence:
            for personId, person in self.presence[locationId].items():
                people.append(person)
        
        return people
            
        
    def newPersonInLocation(self, person, location):
        BluenetEventBus.emit(CloudTopics.personEnteredLocation, {"locationId": location["id"], "name": location["name"], "person": person})
    
    def personLeftLocation(self, person, location):
        BluenetEventBus.emit(CloudTopics.personLeftLocation, {"locationId": location["id"], "name": location["name"], "person": person})
    
    
    