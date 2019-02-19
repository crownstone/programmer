from enum import Enum


class SystemCloudTopics(Enum):
    stoneDownloadedFromCloud = "stoneDownloadedFromCloud"  # used to tell the rest of the system that the cloud module downloaded data on a Crownstone
    presenceInLocationDownloadedFromCloud = "presenceInLocationDownloadedFromCloud"  #