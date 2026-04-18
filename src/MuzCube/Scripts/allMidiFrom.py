from os import listdir
from os.path import isfile, join
def allMidi(mypath):
    onlyfiles = [f for f in listdir(mypath) if isfile(join(mypath, f))]
    onlytxtfiles=[]
    for i in range(len(onlyfiles)):
        if(".txt" in onlyfiles[i] and not "[]" in onlyfiles[i]):
            onlytxtfiles.append(onlyfiles[i])
    return onlytxtfiles