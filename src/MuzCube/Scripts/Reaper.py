import reapy
#from reaper_python import *
import base64
import re
def splitEvt(allEvt):
    noEvt = []
    sysexEvt = []
    scob = False
    sysex = False
    evt = ""
    for str in allEvt:
        if scob:
            evt+= " " + str
        if str[0] == "<":
            scob = True
            evt += str[1:]
        if str[-1] == ">":
            scob = False
            evt += " " + str[:-1]
            if evt[0] == "X":
                sysexEvt.append(evt)
            else:
                noEvt.append(evt)
            evt = ""
            continue
    return [sysexEvt,noEvt]
def getChunk(item):
    chunk = ""     # Get, not Set
    maxlen = 1024*1024  # max num of chars to return. I don't even know whether the function actually is able to return that length, but I saw this somewhere elso and thought "What the heck!"
    (bool, item, chunk, maxlen) = RPR_GetSetItemState(item, chunk, maxlen)
    return chunk
def editorGet():
    midieditor = RPR_MIDIEditor_GetActive()
    return RPR_MIDIEditor_GetTake(midieditor)
def textEvtList(item):
    TakeCount = RPR_CountTakes(item)
    Takeidx = 0
    while Takeidx < TakeCount:
        curTake = RPR_GetMediaItemTake(item, Takeidx)
        if curTake == Take:  # comparing take pointers to find out the take index by count
            IsTake = Takeidx + 1
        Takeidx += 1
    chunk = getChunk(item)
    takes = re.split("<SOURCE ", chunk)
    chunkSplitCount = len(takes)
    CurrentTake = takes[IsTake]
    CutEnd = re.split("\nGUID", CurrentTake)
    TrimEnd = CutEnd[0]
    CutStart = re.split("}\n", TrimEnd) # splits after the POOLEDEVTS line Need to do better, breaks if other lines get added by Cockos. maybe check lines for e/em/x/xm and work on those only?
    EventsPart = CutStart[1]
    return EventsPart
def parseSysex(messege):
   # bites = base64.b64decode(messege)
  #  str = bites.decode("ISO-8859-1")
   # print(str)
    spl = messege.split('"')
    str = ""
    str2= ""
    if len(spl) == 3:
        print(spl[2][3:])
        bites = base64.b64decode(spl[2])
        str = bites.decode("ISO-8859-1")
        str2 = spl[1]
    else:
        spl2 = re.split(r"[ \n]",messege)
        out = ""
        bol = False
        for s in spl2:
            if s[0] == "/":
                out += s[2:]
                bol = True
            if bol:
                out += s
        print(out)
        bites = base64.b64decode(out)
        str = bites.decode("ISO-8859-1")
    return (str,str2)
    #tuple =  re.split(r" (<=[^\"])",messege)
print(parseSysex('<X 240 0 0 0 1 "Exal greka cherez recu"\n' +
                                                       '/wFFeGFsIGdyZWthIGNoZXJleiByZWN1\n' +
'>\n'))
print(parseSysex('X 0 0 ' +
                '/w9OT1RFIDAgNTEgdGV4dCAidmlkaXQgZ3JlY2EgdiByZWtlIHJhaw=='
                ' Ig=='
                ))
notationDict = {}

'''
Take = editorGet()
it = RPR_GetMediaItemTake_Item(Take)

EventsPart = textEvtList(it)
allEvt = EventsPart.split("\n")

print(noEvt)
RPR_ShowConsoleMsg(EventsPart + "\n")  #just so to show up and do something :D ... at this point editing the data, afterwards recreating the whole new item state chunk and finally send it back wo
'''