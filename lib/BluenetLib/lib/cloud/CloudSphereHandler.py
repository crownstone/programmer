import hashlib
import requests

from BluenetLib._EventBusInstance            import BluenetEventBus
from BluenetLib.lib.cloud.CloudBase          import CloudBase
from BluenetLib.lib.topics.SystemCloudTopics import SystemCloudTopics
from BluenetLib.lib.topics.SystemTopics      import SystemTopics

from threading import Timer

class CloudSphereHandler(CloudBase):
    
    
    def __init__(self, sphereId):
        super().__init__()

        self.sphereId = sphereId
        self.sphereData = None

        self.pendingTimer = None
        self.pollingEnabled = False
        
        BluenetEventBus.subscribe(SystemTopics.cleanUp, lambda x: self.stopPollingPresence())
    
    def init(self):
        self.sphereData = self.getSphereData()
    
    def getSphereData(self):
        r = requests.get('https://my.crownstone.rocks/api/Spheres/' + self.sphereId + "?access_token=" + self.accessToken)

        sphereData = None
        if r.status_code == 200:
            reply = r.json()

            sphereData = {
                "name": reply["name"],
                "cloudId": reply["id"],
                "iBeaconUUID": reply["uuid"]
            }
        else:
            print(r.text)
            print("Could not get Sphere data")
    
        return sphereData
    
    def getStones(self):
        r = requests.get('https://my.crownstone.rocks/api/Stones?access_token='+self.accessToken)
        stones = []
        
        if r.status_code == 200:
            reply = r.json()
            
            for stone in reply:
                if stone["sphereId"] == self.sphereId:
                    stoneData = {
                        "id": stone["uid"],
                        "name": stone["name"],
                        "cloudId": stone["id"],
                        "address": stone["address"],
                        "type": stone["type"],
                        "dimmingEnabled": stone["dimmingEnabled"],
                        "major": stone["major"],
                        "minor": stone["minor"],
                        "firmwareVersion": stone["firmwareVersion"],
                    }
                    
                    BluenetEventBus.emit(SystemCloudTopics.stoneDownloadedFromCloud, stoneData)
                    stones.append(stone)
        else:
            print(r.text)
            print("Could not get Stones")
        
        return stones

    def getLocations(self):
        r = requests.get('https://my.crownstone.rocks/api/Spheres/' + self.sphereId + '/ownedLocations?access_token=' + self.accessToken)
        locations = []
    
        if r.status_code == 200:
            reply = r.json()
        
            for location in reply:
                locations.append({"id": location["uid"], "cloudId": location['id'], "name": location["name"]})
        else:
            print(r.text)
            print("Could not get locations")
    
        return locations
    

    def getKeys(self):
        r = requests.get('https://my.crownstone.rocks/api/users/' + self.userId + '/keys?access_token=' + self.accessToken)
    
        if r.status_code == 200:
            reply = r.json()
        
            for keySet in reply:
                if keySet["sphereId"] == self.sphereId:
                    return keySet["keys"]
        else:
            print(r.text)
            print("Could not get keys")
            
            
    
    def startPollingPresence(self, interval=10, firstRun=True):
        if interval < 10:
            interval = 10
            print("Forcing presence polling interval back to 10 to avoid overloading server.")
        
        # start with a syncing run for the presenceManager.
        if firstRun:
            self.getPresence()
        
        self.pollingEnabled = True
        self.pendingTimer = Timer(interval, lambda: self._presencePoller(interval))
        self.pendingTimer.start()
    
    
    def _presencePoller(self, interval):
        self.getPresence()
        if self.pollingEnabled:
            self.startPollingPresence(interval, False)
        elif self.pendingTimer is not None:
            self.pendingTimer.cancel()
            
        
    def getPresence(self):
        r = requests.get('https://my.crownstone.rocks/api/Spheres/' + self.sphereId + '/ownedLocations?filter=%7B%22include%22%3A%22presentPeople%22%7D&access_token=' + self.accessToken)

        locations = []
        if r.status_code == 200:
            reply = r.json()
            
            for location in reply:
                presentPeople = []
                for person in location["presentPeople"]:
                    presentPeople.append({"id": person["id"], "email":person["email"], "name": person["firstName"] + " " + person["lastName"]})
                locationData = {"cloudId": location["id"], "id": location["uid"], "name": location["name"], 'presentPeople': presentPeople}
                locations.append(locationData)
                BluenetEventBus.emit(SystemCloudTopics.presenceInLocationDownloadedFromCloud, locationData)
        else:
            print(r.text)
            print("Could not get presence")

        return locations
        
    
    def stopPollingPresence(self):
        self.pollingEnabled = False
        if self.pendingTimer is not None:
            self.pendingTimer.cancel()
    
            
    
    


            
    
    

    





       