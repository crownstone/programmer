from BluenetLib.lib.cloud.CloudBase import CloudBase
from BluenetLib.lib.cloud.CloudSphereHandler import CloudSphereHandler


class CloudHandler(CloudBase):
    
    def __init__(self):
        super().__init__()
    
    def getSphereHandler(self, sphereId):
        sphereHandler = CloudSphereHandler(sphereId)

        self._loadDataIntoSphereHandler(sphereHandler)
        sphereHandler.init()
        return sphereHandler
    
    
    def getSphereHandlerByName(self, sphereName):
        spheres = self.getSpheres()
        
        for sphere in spheres:
            if sphere["name"] == sphereName:
                return self.getSphereHandler(sphere["id"])
        
        return None
    
    
    def _loadDataIntoSphereHandler(self, sphereHandler):
        sphereHandler.email = self.email
        sphereHandler.password = self.password
        sphereHandler.sha1Password = self.sha1Password
        sphereHandler.accessToken = self.accessToken
        sphereHandler.userId = self.userId
        sphereHandler.initialized = self.initialized
    
        return sphereHandler
    
    def getStones(self, sphereId):
        pass

    def getLocations(self, sphereId):
        pass

    def getKeys(self, sphereId):
        pass
        
    def getPresence(self, sphereId):
        pass
    
    def pollPresence(self, sphereId):
        pass

    
    
    
            
    
    


            
    
    

    





       