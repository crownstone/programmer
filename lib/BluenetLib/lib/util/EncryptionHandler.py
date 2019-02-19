import random

import math
import pyaes

from BluenetLib.Exceptions import BluenetBleException, BleError
from BluenetLib.lib.core.modules.BluenetSettings import UserLevel
from BluenetLib.lib.util.Conversion import Conversion


BLOCK_LENGTH             = 16
NONCE_LENGTH             = 16
SESSION_DATA_LENGTH      = 5
SESSION_KEY_LENGTH       = 4
PACKET_USER_LEVEL_LENGTH = 1
PACKET_NONCE_LENGTH      = 3
CHECKSUM                 = 0xcafebabe

BLUENET_ENCRYPTION_TESTING = False

class SessionData:
    def __init__(self, sessionData):
        self.sessionNonce = None
        self.validationKey = None
        
        if len(sessionData) != SESSION_DATA_LENGTH:
            raise BluenetBleException(BleError.INVALID_SESSION_DATA, "Invalid Session Data")
        
        self.sessionNonce  = [0] * SESSION_DATA_LENGTH
        self.validationKey = [0] * SESSION_KEY_LENGTH
        
        for i in range(0,SESSION_KEY_LENGTH):
            self.sessionNonce[i]  = sessionData[i]
            self.validationKey[i] = sessionData[i]
        
        self.sessionNonce[SESSION_DATA_LENGTH-1] = sessionData[SESSION_DATA_LENGTH-1]
        
       

class EncryptedPackage:
    
    def __init__(self, dataArray):
        self.nonce = None
        self.userLevel = None
        self.payload = None
        
        prefixLength = PACKET_NONCE_LENGTH + PACKET_USER_LEVEL_LENGTH
        # 20 is the minimal size of a packet (3+1+16)
        if len(dataArray) < 20:
            raise BluenetBleException(BleError.INVALID_ENCRYPTION_PACKAGE, "Invalid package for encryption. It is too short (min length 20) got " + str(len(dataArray)) + " bytes.")

        self.nonce = [0] * PACKET_NONCE_LENGTH
        
        for i in range(0, PACKET_NONCE_LENGTH):
            self.nonce[i] = dataArray[i]
            
        if dataArray[PACKET_NONCE_LENGTH] > 2 and dataArray[PACKET_NONCE_LENGTH] != UserLevel.setup.value:
            raise BluenetBleException(BleError.INVALID_ENCRYPTION_USER_LEVEL, "User level in read packet is invalid:" + str(dataArray[PACKET_NONCE_LENGTH]))
        
        try:
            self.userLevel = UserLevel(dataArray[PACKET_NONCE_LENGTH])
        except ValueError:
            raise BluenetBleException(BleError.INVALID_ENCRYPTION_USER_LEVEL, "User level in read packet is invalid:" + str(dataArray[PACKET_NONCE_LENGTH]))
        
        payload = [0] * (len(dataArray) - prefixLength)
        for i in range(0, (len(dataArray) - prefixLength)):
            payload[i] = dataArray[i + prefixLength]
            
        if len(payload) % 16 != 0:
            raise BluenetBleException(BleError.INVALID_ENCRYPTION_PACKAGE, "Invalid size for encrypted payload")
        
        self.payload = payload


class EncryptionHandler:
    
    @staticmethod
    def decryptSessionNonce(inputData, key):
        if len(inputData) == 16:
            decrypted = EncryptionHandler.decryptECB(inputData, key)
            checksum = Conversion.uint8_array_to_uint32(decrypted)
            if checksum == CHECKSUM:
                return [decrypted[4], decrypted[5], decrypted[6], decrypted[7], decrypted[8]]
            else:
                raise BluenetBleException(BleError.COULD_NOT_VALIDATE_SESSION_NONCE, "Could not validate the session nonce.")
    
        else:
            raise BluenetBleException(BleError.COULD_NOT_READ_SESSION_NONCE, "Could not read session nonce, maybe encryption is disabled?")
    
    
    @staticmethod
    def decryptECB(uint8Array, key):
        aes = pyaes.AESModeOfOperationECB(key)
        
        stringPayload = "".join(chr(b) for b in uint8Array)
        
        decrypted = aes.decrypt(stringPayload)
        
        return decrypted


    @staticmethod
    def encryptECB(uint8Array, key):
        aes = pyaes.AESModeOfOperationECB(key)
    
        stringPayload = "".join(chr(b) for b in uint8Array)
    
        encrypted = aes.encrypt(stringPayload)
    
        return encrypted


    @staticmethod
    def decryptCTR(data, packetNonce, sessionNonce, key):
        IV = EncryptionHandler.generateIV(packetNonce, sessionNonce)
    
        stringPayload = "".join(chr(b) for b in data)
    
        aes = pyaes.AESModeOfOperationCTR(key, counter=IVCounter(IV))
    
        decryptedData = aes.decrypt(stringPayload)
    
        return decryptedData


    @staticmethod
    def decrypt(data, settings):
        if settings.sessionNonce is None:
            raise BluenetBleException(BleError.NO_SESSION_NONCE_SET, "Can't Decrypt: No session nonce set")
    
        if settings.userLevel == UserLevel.unknown:
            raise BluenetBleException(BleError.NO_ENCRYPTION_KEYS_SET, "Can't Decrypt: No encryption keys set.")
        
        #unpack the session data
        sessionData = SessionData(settings.sessionNonce)
        package = EncryptedPackage(data)
        
        key = EncryptionHandler._getKeyForLevel(package.userLevel, settings)
    
        # decrypt data
        decrypted = EncryptionHandler.decryptCTR(package.payload, package.nonce, sessionData.sessionNonce, key)
        
        return EncryptionHandler._verifyDecryption(decrypted, sessionData.validationKey)
    
    
    @staticmethod
    def _verifyDecryption(decrypted, validationKey):
        # the conversion to uint32 only takes the first 4 bytes
        if Conversion.uint8_array_to_uint32(decrypted) == Conversion.uint8_array_to_uint32(validationKey):
            # remove checksum from decryption and return payload
            result = [0] * (len(decrypted) - SESSION_KEY_LENGTH)
            for i in range(0,len(result)):
                result[i] = decrypted[i+SESSION_KEY_LENGTH]
            return result
    
        else:
            raise BluenetBleException(BleError.ENCRYPTION_VALIDATION_FAILED, "Failed to validate result, Could not decrypt")
            
    
    @staticmethod
    def getRandomNumber(testing=False):
        if testing:
            return 128
        return random.randint(0,255)


    @staticmethod
    def encryptCTR(dataArray, packetNonce, sessionNonce, key):
        sessionData = SessionData(sessionNonce)
    
        IV = EncryptionHandler.generateIV(packetNonce, sessionNonce)
        
        # calculate the amount of blocks
        amountOfBlocks = int(math.ceil(float(SESSION_KEY_LENGTH + len(dataArray)) / float(BLOCK_LENGTH)))
    
        # create buffer that is zero padded
        paddedPayload = [0] * amountOfBlocks * BLOCK_LENGTH
    
        # fill the payload with the key and the data
        for i in range(0, SESSION_KEY_LENGTH):
            paddedPayload[i] = sessionData.validationKey[i]
    
        for i in range(0, len(dataArray)):
            paddedPayload[i + SESSION_KEY_LENGTH] = dataArray[i]
    
        stringPayload = "".join(chr(b) for b in paddedPayload)
    
        aes = pyaes.AESModeOfOperationCTR(key, counter=IVCounter(IV))
    
        encryptedData = aes.encrypt(stringPayload)
        
        return encryptedData
    
    @staticmethod
    def encrypt(dataArray, settings):
        if settings.sessionNonce is None:
            raise BluenetBleException(BleError.NO_SESSION_NONCE_SET, "Can't Decrypt: No session nonce set")
    
        if settings.userLevel == UserLevel.unknown:
            raise BluenetBleException(BleError.NO_ENCRYPTION_KEYS_SET, "Can't Decrypt: No encryption keys set.")

        packetNonce = [0] * PACKET_NONCE_LENGTH
        # create a random nonce
        for i in range(0, PACKET_NONCE_LENGTH):
            packetNonce[i] = EncryptionHandler.getRandomNumber()
        
        key = EncryptionHandler._getKey(settings)
        encryptedData = EncryptionHandler.encryptCTR(dataArray, packetNonce, settings.sessionNonce, key)
    
        result = packetNonce + [settings.userLevel.value]
        
        for byte in encryptedData:
            result.append(byte)
    
        return bytes(result)
            
    
    @staticmethod
    def _getKey(settings):
        return EncryptionHandler._getKeyForLevel(settings.userLevel, settings)
        
    @staticmethod
    def _getKeyForLevel(userLevel, settings):
        if settings.initializedKeys == False and userLevel != UserLevel.setup:
            raise BluenetBleException(BleError.NO_ENCRYPTION_KEYS_SET, "Could not encrypt: Keys not set.")
    
        key = None
        if userLevel == UserLevel.admin:
            key = settings.adminKey
        elif userLevel == UserLevel.member:
            key = settings.memberKey
        elif userLevel == UserLevel.guest:
            key = settings.guestKey
        elif userLevel == UserLevel.setup:
            key = settings.setupKey
        else:
            raise BluenetBleException(BleError.NO_ENCRYPTION_KEYS_SET, "Could not encrypt: Invalid key for encryption.")
    
        if key is None:
            raise BluenetBleException(BleError.NO_ENCRYPTION_KEYS_SET, "Could not encrypt: Keys not set.")
    
        return key
        
    
    @staticmethod
    def generateIV(packetNonce, sessionData):
        if len(packetNonce) != PACKET_NONCE_LENGTH:
            raise BluenetBleException(BleError.INVALID_SESSION_NONCE, "Invalid size for session nonce packet")
        
        IV = [0] * NONCE_LENGTH
        
        # the IV used in the CTR mode is 8 bytes, the first 3 are random
        for i in range(0,PACKET_NONCE_LENGTH):
            IV[i] = packetNonce[i]
        
        # the IV used in the CTR mode is 8 bytes, the last 5 are from the session data
        for i in range(0,SESSION_DATA_LENGTH):
            IV[i + PACKET_NONCE_LENGTH] = sessionData[i]
            
        return IV
    
    
class IVCounter(object):
    """
        A counter object for the Counter (CTR) mode of operation.

       To create a custom counter, you can usually just override the
       increment method.
    """
    
    def __init__(self, initialList):
        
        # Convert the value into an array of bytes long
        self._counter = initialList
    
    value = property(lambda s: s._counter)
    
    def increment(self):
        self._counter[len(self._counter)-1] += 1

        