import sys, os
from pathlib import Path

# this is used for profiling
basePath = sys.path[0]
# if sys.path[0] == '':
#     basePath = "~/pi/workspace/share/"


# Because python searches for local imports in the sys.path folders, we need to add the root folder of this project to
# the sys.path. Since this path.py will be called from the folder /<projectRoot>/examples, we need to go one dir up to
# get the project root.



for item in os.listdir(basePath):
    if os.path.isdir(basePath + "/" + item):
        if item[0] != ".":
            # print("ADDING", basePath + "/" + item)
            sys.path.append(basePath + "/" + item)


for item in os.listdir(basePath + "/vendor/"):
    if os.path.isdir(basePath + "/vendor/" + item):
        if item[0] != ".":
            # print("ADDING", basePath + "/vendor/" + item)
            sys.path.append(basePath + "/vendor/" + item)

# add the stringified parent folder to the sys.path so our imports can be evaluated.

# sys.path.append(str(parentsOfScriptFolder[0]))
