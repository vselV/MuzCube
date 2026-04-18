import reapy
from reapy import reascript_api as RPR
import re
# Получаем текущий проект

def Stroks(Take):
    it = RPR.GetMediaItemTake_Item(Take)
    TakeCount = RPR.CountTakes(it)
    Takeidx = 0
    while Takeidx < TakeCount:
        curTake = RPR.GetMediaItemTake(it, Takeidx)
        if curTake == Take:
            IsTake = Takeidx + 1
        Takeidx += 1
    chunk = ""
    maxlen = 1024 * 1024
    (bool, it, chunk, maxlen) = RPR.GetSetItemState(it, chunk, maxlen)
    takes = re.split("<SOURCE ", chunk)
    chunkSplitCount = len(takes)
    CurrentTake = takes[IsTake]
    CutEnd = re.split("\nGUID", CurrentTake)
    TrimEnd = CutEnd[0]
    CutStart = re.split("}\n",
                        TrimEnd)
    EventsPart = CutStart[1]
    return EventsPart
