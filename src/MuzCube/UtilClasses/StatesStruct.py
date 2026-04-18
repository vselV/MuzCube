

class StatesStruct():
    def _init_(self,tupleState,lenText):
        self.dictState={}
        self.lenText=lenText
        self.fill(tupleState)
    def fill(self,tupleState):
        for pos, stack in tupleState:
            self.dictState[pos]=stack
    def getStack(self,pos):
        i = pos
        while True:
            if self.dictState.get(i) is not None:
                return self.dictState.get(i)
            i -= 1
    def getNextStack(self,pos):
        i = pos
        while True:
            if self.dictState.get(i) is not None:
                return self.dictState.get(i)
            i += 1
    def put(self,pos,length,newTuple):
        outIn = self.getStack(pos)
        out = outIn
        i = self.lenText
        for k in range(self.lenText - pos):
            if self.dictState.get(i) is not None:
                self.dictState[i + length] = self.dictState.get(i)
                del self.dictState[i]
            i -= 1
        for pos, stack in newTuple:
            self.dictState[pos]=stack
            out = stack
        self.lenText += length
        return out == outIn
    def delete(self,pos,length):
        outIn = self.getStack(pos)
        out = self.getStack(pos+length)
        self.lenText=self.lenText - length
        i=pos
        for k in range(length):
            if self.dictState.get(i) is not None:
                del self.dictState[i]
            i += 1
        for k in range(self.lenText - pos):
            if self.dictState.get(i) is not None:
                self.dictState[i - length] = self.dictState.get(i)
                del self.dictState[i]
            i -= 1
        return out == outIn
    def replace(self,pos,lengthDel,lengthPut,newTuple):
        a = self.delete(pos,lengthDel)
        b = self.put(pos,lengthPut,newTuple)
        return a and b
class sameStruct():
    def _init_(self,Text):
        py=0