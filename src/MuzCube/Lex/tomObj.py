import random
from dataclasses import dataclass
from typing import List

from src.MuzCube.Scripts import addReapy
from midiutil import MIDIFile
import math
from pathlib import Path
import re
import src.MuzCube.UtilClasses.mClass

deafile = MIDIFile(1)
namefileDef = "NOINTERPR"

@dataclass
class NoteData():
    text:str = "0"
    root:str = "0"
    vel:int = 100
    note_p: int = 60
    pitch_wheel : int =0
    y_pose : float = 0
    x_start : float = 0
    x_end : float = 0
@dataclass
class ChordData():
    notes: List[NoteData]
    text:str = "0"
    root:str = "0"
@dataclass
class ArpeggioData():
    chord:ChordData
    text:str = "0"
    root:str = "0"
def ypose(note_p,pitch):
    return (note_p * 4096 + pitch) / 4096 * 50
def toppx(beats):
    return beats * 200
def note_prod(note_pitch,pitch,time_ppx,len_ppx,vel,text):
    note = NoteData(note_p = note_pitch, pitch_wheel=pitch,
                    x_start=time_ppx,x_end=time_ppx+len_ppx,
                    vel=vel,text=text,y_pose = ypose(note_pitch,pitch))
    return note
class toMidi():
    def __init__(self,namefile=namefileDef,track=0,MyMIDI = MIDIFile(1),**kwargs):
        self.MyMIDI=MyMIDI
        self.namefile = namefile
        self.track = track
        self.kwargs = kwargs
        self.reInit(kwargs)
    def reInit(self,kwargs):

        self.midi =MIDIFile(1)
        self.pohu=kwargs.get("pohu",False)
        self.chanMax = kwargs.get("chanMax",16)

        self.reapyBol=kwargs.get("reapyBol",False)
        self.take=kwargs.get("reapyData",False)
        self.oneStr=kwargs.get("oneStr",False)

        self.dictionary = {"": ""}
        self.dictChords = {"": ""}
        self.TempDict={"Default": ["0","2","0.1","-1","1","-1.1","1.1"]}
        self.arpegDict={"":""}
        self.paternList={"":""}
        self.special=["c",'f','e','t']
        self.chKwargs={}
        self.tempKwargs={"Default":{}}
        self.dictionaryVal = {"!!":8,"!":4,"@":2,"#": 1,"$":0.5,"%":0.25,"^":0.125,"&":0.0625}
        self.simpleNumbers=[2,3,5,7,11,13,17,19,23]
        self.oneCent=math.pow(2,1/1200)
        self.conceptOct=2
        self.finalmass=[]
        self.FromI=1
        self.actualSame=""
        self.simplCom=["oct","inst","root","fix","turn","edo","valOct","chan","vel","getState","setState","setBase"]
        self.stateMent=["rootm","currentLen","octave","instr","veloc","EDO","EDOconst","GlobalChanel","timePoint"]

        self.pythonKeyWords = ["pyGlobal","pyLocal","endPy"]

        self.noSCOB = ["fix","turn","getState","setState","unBind"]
        self.withArg = ["vel","root","chan","reLen","setScale","edo","oct","valOct"]
        self.withArgNotStr = ["chan","tp","edo","oct","valOct","setBase"]
        self.withArgText = ["vel","root","chan","reLen","setScale","edo","oct","valOct"]
        self.GlobalPythonContext=""
        self.currentTemp=""
        self.tempP=True
        self.state=[]
        self.separateMass=["+","-",":","v","=","x"]
        self.variables = ["s"]
        self.count=1
        self.currentTemp="Default"

        self.changeLen=False
        self.LastLen=0
        self.bindPattern=""
        self.Binded=False

        self.changeOct=False
        self.lastOct=0

        self.changeVel=False
        self.lastVel=80

        self.changeEdo=False
        self.lastEdo=12

        self.conOctCh=False
        self.lConOct=2

        self.conficent=1

        self.currentLen=1
        self.instr=0
        self.line=0
        self.sameB=False
        self.mus=[]
        self.fromStr=kwargs.get("fromStr",False)
        self.lineStr=kwargs.get("line","")
        self.active = self.namefile != namefileDef
        if(not self.fromStr and self.active):
            self.file = open(self.namefile, 'r')
            self.mus =self.file.readlines()
        else:
            self.mus= self.lineStr.split("\n")
        self.tempo=120

        self.re_tempo = self.tempo
        self.re_sig = "4/4"

        self.note=60
        self.rootm="0"
        self.octave=0
        self.timeInBeats=0

        self.pause=False
        self.veloc=80
        self.TextVis=""
        self.EDO=12
        self.EDOconst=math.pow(2,1/self.EDO)
        #MyMIDI = MIDIFile(1)  # One track, defaults to format 1 (tempo track is created
        self.GlobalChanel=0
        self.timePoint=0

        self.dLong=1
        self.dLongBoll=False
        self.pointT = 0;
        self.pointCL = 0;
        self.Random=False
        if self.active:
            if "#" in self.mus[0]:
                if (not self.pohu):
                    return False
                else:
                    self.mus[0] = self.mus[0].replace("#", "")
            if self.mus[0][0] == ":":
                self.TextVis += self.mus[0]
                self.param = self.mus[0][1:].split(";")
                self.tempo = float(self.param[0])
                if (len(self.param) > 1):
                    self.note = int(self.param[1])
                self.line += 1
        self.MyMIDI.addTempo(0, 0, self.tempo)
        self.midi.addTempo(0, 0, self.tempo)
        self.MyMIDI.addTrackName(self.track, 0, self.namefile)
        self.midi.addTrackName(0, 0, self.namefile)
        self.GlobalPy = False
        self.Py = False
        self.pyArg = 0
        self.localPy = ""
        self.start=kwargs.get("start",True)
        if self.start and self.active:
            self.startAll()
            self.output()

        self.only_note_data = False
        self.note_data_production = []

    def set_only_note_data(self,val = True):
        self.only_note_data = val
    def LoadFiles(self,files):
        for f in files:
            self.load(f)
    def get_inter_data(self):
        return mClass.InterData(self.rootm,self.conceptOct,self.octave)
    def get_coef(self):
        return self.re_tempo/self.tempo
    def TempoSig(self,temp,sig):
        self.re_tempo = self.tempo = temp
        self.re_sig = sig
        if self.reapyBol:
            addReapy.addTempo(self.re_tempo, sig, self.timeInBeats * 960)


    def convertNormal(self,command):
        if self.reapyBol:
            addReapy.addCommand(self.take, command, self.timeInBeats * 960)
        sp=command.split(":")
        name=sp[0].replace(" ","").replace("\t","")
        if(":" in command):
            if(name == "vel" or name == "reLen" or name == "oct"):
             #   if(re.search(r"[\+\/\-*]",sp[1].replace(" ",""))):
                    #print()
              #      return name+"('"+sp[1]+"')"
             #   else:
                return name+"("+sp[1]+")"
            elif (name == "inst"):
                if(sp[1].replace(" ","")=="rand"):
                    return name+"('"+sp[1]+"')"
                else:
                    return name+"("+sp[1]+")"
            elif (name == "root" or name=="setScale" or name=="noteBind"):
                return name+"('"+sp[1]+"')"
            elif (name == "add" or name =="SM"):
                return name+"('"+sp[1]+"')"
            elif name in self.withArgNotStr:
                return name+"("+sp[1]+")"
        elif(">" in command):
            sp=command.split(">")
            name=sp[0].replace(" ","").replace("\t","")
            if(name == "add"):
               # print(name + "('"+sp[1]+"', s=1)")
                return name + "('"+sp[1]+"', s=1)"
        else:
            if(name in self.noSCOB):
                return name + "()"
        return command
       # else:
    def NoteConstruct(self,massInt):
        strAns=""
        for i in massInt:
            strAns+="."+str(i)
        return strAns[1:]
    def pyContext(self,str):
        self.GlobalPythonContext+=str
        ###########################################ssssssssssssssssssssssssAAAAAAAAAAAAAAAA
    def pythonEval(self,StrCode,**kwargs):
        addNote = self.addNote
        load = self.load
        fix = self.fix
        turn = self.turn
        edo = self.edo
        inst = self.inst
        vel = self.vel
        valOct = self.valOct
        chan = self.chan
        SM = self.SM
        reLen = self.reLen
        getState = self.getState
        setState = self.setState
        noteBind = self.noteBind
        unBind = self.unBind
        setScale = self.setScale
        swap = self.swap
        tp = self.tp
        root = self.root
        oct = self.oct
        arpeg = self.arpeg
        chord = self.chord
        pattern = self.pattern
        scale = self.scale
        setBase = self.setBase
        
        if(kwargs.get("var",False)):
            veloc=self.veloc
            rootm=self.rootm
            octave=self.octave
            edo=self.edo
            currentLen=self.currentLen
            timeInBeats=self.timeInBeats
            conceptOct=self.conceptOct
            timePoint=self.timePoint
            eval(self.GlobalPythonContext+StrCode)
        else:
            eval(self.GlobalPythonContext+StrCode)
    def setDeaf(self):
        self.vel(80)
        self.edo(12)

    def valOct(self,nOct):
        self.conceptOct=nOct
    def inst(self,p):
        if type(p) is int:
            self.instr=p
        if type(p) is str:
            if(p=="rand"):
                self.Random=not self.Random
        if(self.Random and p==-1):
            self.instr=random.randint(0, 127)
    def setBase(self,note):
        self.note = note
    def chord(self,name,mass,*args,**kwargs):
        self.chKwargs[name]=kwargs
      #  lEdo=kwargs.get("edo",-1)
      #  octCh=kwargs.get("oct",-1)
        if type(mass) is list:
            self.dictChords[name]=mass
        if type(mass) is str:
            self.dictChords[name]=mass.split(" ")
    def chan(self,*args):
        if(len(args)==0):
            self.GlobalChanel+=1
        else:
            self.GlobalChanel=args[0]
    def fix(self):
        self.timePoint=self.timeInBeats
    def turn(self):
        self.timeInBeats=self.timePoint
    def loadEval(self,aS,mus):
        chord=self.chord
        pattern=self.pattern
        scale=self.scale
        arpeg = self.arpeg
        if(aS!=""):
            mSp=re.split(r"\( *",mus,1)
            simb=mSp[1][0]
            stroc=mSp[0]+"("+simb+aS+"."+mSp[1][1:]
            eval(stroc)
        else:
            eval(mus)
    def load(self,file,**kwargs):
        chord = self.chord
        pattern = self.pattern
        scale = self.scale
        arpeg=self.arpeg
        aS=kwargs.get("as","")
        ro=kwargs.get("root",0)
        sk=False
        lod=self.namefile.split("/")
        dir=""
        for i in range(len(lod)-1):
            dir+=lod[i]
        if dir != "": 
            nf=dir+"/"+file
        else:
            nf=file
        if(ro==1):
            nf=file
        h=open(nf,"r")
        mus=h.readlines()
        for i in range(len(mus)):
            pk=mus[i].replace("\n","")
            spl=mus[i].split(";")
            for j in range(len(spl)):
                if("chord" in spl[j].split("(")[0]):
                    self.loadEval(aS,mus[i])
                if("pattern" in spl[j].split("(")[0]):
                    self.loadEval(aS,spl[j])
                if("scale" in spl[j].split("(")[0]):
                    self.loadEval(aS,spl[j])
                if("arpeg" in spl[j].split("(")[0]):
                    self.loadEval(aS,spl[j])
                if(pk==""):
                    continue
                if("same" == spl[j].replace(" ","")):
                    sk=True
                    continue
                if("end" == spl[j].split(":")[0].replace(" ","")):
                    sk=False
                    self.end(mus[i])
                    continue
                if(sk):
                    self.same(mus[i])
        h.close()
    def oct(self,o,*args,**kwargs):
        last=kwargs.get("last",False)
        char=kwargs.get("char","")
        if(last):
            self.changeOct=True
            self.lastOct=self.octave
            if(o==""):
                self.octave=self.octave+int(char+"1")
            else:
                self.octave=self.octave+int(char+o)
        else:
            if(type(o) is str):
                k=eval("octave"+o)
                self.octave=k
            else:
                self.octave=o
       # print(self.octave)
    ######################3
    def notSpec(self,note):
        for c in self.special:
            if c in note:
                return False
        return True
    def root(self,r):
        if(r[0]=="~"):
            dtr=r[1:]
            if(self.notSpec(dtr) and self.notSpec(self.rootm)):

                #print(dtr)
                nm1=dtr.split(".")
                nm2=self.rootm.split(".")
                jk=max(len(nm1),len(nm2))
                lMas=[]
                strK=""
                for i in range(jk):
                    c=0
                    if(i<len(nm1)):
                        c+=int(nm1[i])
                    if(i<len(nm2)):
                        c+=int(nm2[i])
                    lMas.append(c)
                for i in range(jk):
                    strK+="."+str(lMas[i])
                strK=strK[1:]
                self.rootm=strK
            else:
                self.rootm=str(self.fcent(self.rootm)+self.fcent(dtr))+"c"
        else:
            self.rootm=r
       # print(self.rootm)
    def tp(self,time):
        self.timeInBeats=self.time
    def same(self,l):
        self.actualSame+=l+"\n"
    def vel(self,v,*args,**kwargs):
        last=kwargs.get("last",False)
        if type(v) is str:
            p=eval("veloc"+v)
            self.veloc=min(127,p)
            self.veloc=max(0,self.veloc)
         #   print(self.veloc)
            return
        if(last):
            self.lastVel=self.veloc
            self.changeVel=True
            self.veloc=v
        else:
            self.veloc=v
    # print(actualSame)
    def reLen(self,com):
        if type(com) is str:
            p=eval("self.currentLen"+com)
            self.currentLen=p
            return
        else:
            self.currentLen=com
    def getNum(self,nump):
        if nump=="_":
            self.pause=True
            return 1
        m=nump.split(".")
        intA=1
        for i in range(len(m)):
            intA=intA*math.pow(self.simpleNumbers[self.FromI+i],int(m[i]))
        return intA
    def edo(self,edo):
        self.EDO=edo
        self.EDOconst=math.pow(self.conceptOct,1/self.EDO)

    def tPose(self,num):
        j=num
      #  p=tPoseRot(getNum(rootm))
        while(j>self.conceptOct):
            j=j/self.conceptOct
        while(j<1):
            j=j*self.conceptOct
        return j
    def pattern(self,name,patern):
        self.paternList[name]=patern
    def tPoseRot(self,rootm):
        j=rootm
        while(j>self.conceptOct):
            j=j/self.conceptOct
        while(j<1):
            j=j*self.conceptOct
        return j
    def scale(self,name,strk,**kwargs):
        sort=kwargs.get("sort",0)
        fromEdo = kwargs.get("fromEdo",False)
        tem=[]
        if type(strk) is str:
            tem=strk.split(" ")
        else:
            tem=strk
         ## print(tem,type(strk))
        ftem=[]
        cents = []
        self.getState()
        for st in tem:
            if st != "":
                 ## print(st)
                cents.append(self.fcentOct(st))
                ftem.append(st)
        if sort==1:
            ftem=self.SortTwo(cents,ftem)
        self.setState()
        self.TempDict[name]=ftem
        self.tempKwargs[name]=kwargs
    def fromTmp(self,index,name,**kwargs):
       # ch=kwargs.get("ch",0)
        print(self.TempDict)

        print(self.tempKwargs)
        if(not self.tempP):
            mass=self.dictChords.get(name)
            arg=self.chKwargs.get(name)
            edos=arg.get("edo",12)
            octS=arg.get("oct",2)
            simp_num = arg.get("simp_num",self.simpleNumbers)
        else:
            mass=self.TempDict.get(name)
            arg=self.tempKwargs.get(name)
            print(name,arg)
            edos=arg.get("edo",12)
            octS=arg.get("oct",2)
            simp_num = arg.get("simp_num", self.simpleNumbers)
        a=self.conceptOct
        b=self.EDO
        c = self.simpleNumbers
        self.simpleNumbers = simp_num
        self.edo(edos)
        self.setOct(octS)
        m=self.fcentOct(mass[index%(len(mass))])
        octCh=index//(len(mass))
        self.edo(a)
        self.setOct(b)
        self.simpleNumbers = c
        return m+octCh*int(math.log(octS,self.oneCent))
    def SortTwo(self,base,obj):
        dictL={}
        mp=[]
        for i in range(len(base)):
            dictL[base[i]]=obj
        sort=sorted(base)
        for i in range(len(base)):
            mp.append(dictL.get(sort[i]))
        return mp
    def getScales(self):
        return self.TempDict.keys()
    def getChords(self):
        return self.dictChords.keys()
    def noteBind(self,patternName,**kwargs):
        self.bindPattern=patternName
        self.Binded=True
    def unBind(self):
        self.Binded=False
    def setOct(self,num):
        return num*math.pow(self.conceptOct,self.octave)
    def cents(self,num):
        return math.log(num,self.oneCent)
    def midipith(self,cents):
        return [int(cents)//100,int(cents)%100+(cents-int(cents))]
    def toPith(self,cnt):
        return int(8192/200*cnt)
    def fromEdo(self,step):
        a = step.split("e")
        if len(a) > 1:
            ed = self.EDO
            self.edo(float(a[1]))
            out = math.pow(self.EDOconst,float(a[1]))
            self.edo(ed)
            return out
        fc = float(step.replace("e",""))
        return math.pow(self.EDOconst,fc)
    def inOne(self,mass,str):
        for k in mass:
            if k in str:
                return True
        return False
    def fcent2(self,fc):
        if "f" in fc:
            return self.cents(float(fc.replace("f","")))
        if "c" in fc:
            return int(fc.replace("c",""))
        if "с" in fc:
            return int(fc.replace("с",""))
        if "e" in fc:
            return self.cents(self.fromEdo(fc))
        return self.cents(self.setOct(self.tPose(self.getNum(fc))))
    def fcent(self,fc):
        np=re.split(":|\\+|-|v",fc)
        str=""
        prL=""
        ct=0
        for l in fc:
           # if(l.isdigit()):
            if(l==":" or l=="v" or l=="="):
                break
            if(l=="-" or l=="+"):
                if(prL=="" or prL=="."):
                    str+=l
                    ct+=1
                else:
                    break
            else:
                str+=l
                ct+=1
            prL=l
      #  print(fc[ct:])
        self.interPr(fc[ct:])
     #   print(fc)
       # print(str)
        return self.fcentOct(str)
    def SM(self,name,**kwargs):
        cnt=kwargs.get("n",1)
        com=kwargs.get("cm","")
        st=kwargs.get("st",0)
        cf=kwargs.get("cf",1)
        if(st==1):
            self.getState()
        if(name[0]==":"):
            self.add(name[1:],n=cnt,cm=com,fromSt=True,cf=cf)
        else:
            self.add(name,n=cnt,cm=com,cf=cf)
        if(st==1):
            self.setState()
    def fcentOct(self,fc):
      #  if fc == "":
      #      fc = "0"
        if "f" in fc:
            return self.cents(eval(fc.replace("f","").replace("x","*")))
        if "c" in fc:
            return int(float(fc.replace("c","")))
        if "e" in fc:
            return self.cents(self.fromEdo(float(fc.replace("e",""))))
        if "t" in fc:
            return self.fromTmp(int(fc.replace("t","")),self.currentTemp)
       # print(fc)
        return self.cents(self.tPose(self.getNum(fc)))
    def setScale(self,name,**kwargs):
        ch=kwargs.get("ch",0)
        if(ch==1):
            self.tempP=False
        else:
            self.tempP=True
        self.currentTemp=name
    def arpeg(self,name,listp):
        if type(listp) is list:
            self.arpegDict[name]=listp
        if type(listp) is str:
            self.arpegDict[name]=listp.split(" ")
    def interA(self,strK,p):
        if(p==":"):
            self.setLen(strK,last=True)
        if(p=="+" or p=="-"):
            self.oct(strK,last=True,char=p)
        if(p=="v"):
            self.vel(strK,last=True)
        if(p=="="):
            self.setLen(strK,dLong=True)
    def interPr(self,lin):
        strK=""
        p=""
        for k in lin:
          #  print(k)
            if k in self.separateMass:
                if(p!=""):
                    self.interA(strK,p)
                strK=""
                p=k
            else:
                if p != "":
                    strK+=k
        if(p!=""):
            self.interA(strK,p)
    def setLen(self,h,*args,**kwargs):
        last=kwargs.get("last",False)
        dLongL=kwargs.get("dLong",False)
        if(last):
            self.LastLen=self.currentLen
            self.changeLen=True
        l1="."in h
        l2=".."in h
        t=h.replace(".","").split("t")
        if(dLongL):
            self.dLong=self.dictionaryVal.get(t[0])
            self.dLongBoll=True

        lenm=self.dictionaryVal.get(t[0])
        if(len(t)>1):
            if(len(t[1])>0):
                lenm=lenm/int(t[1])*2
            else:
                lenm=lenm/3*2
        if(l2):
            lenm=lenm+lenm/2+lenm/4
        else:
            if(l1):
                lenm=lenm+lenm/2
        if(dLongL):
            self.dLong=lenm
            self.dLongBoll=True
        else:
            self.currentLen=lenm
    def getState(self):
        self.state=[self.rootm,self.currentLen,self.octave,self.instr,self.veloc,self.EDO,self.EDOconst,self.GlobalChanel,self.timePoint]
    def setState(self):
        self.rootm,self.currentLen,self.octave,self.instr,self.veloc,self.EDO,self.EDOconst,self.GlobalChanel,self.timePoint=self.state
    def swap(self,*args):
        if(len(args)==0):
            self.simpleNumbers=[2,3,5,7,11,13,17,19,23]
            self.conceptOct=2
            return
        a=args[0]
        b=args[1]
        ac=0
        bc=0
        for i in range(len(self.simpleNumbers)):
            if(self.simpleNumbers[i]==a):
                ac=i
            if(self.simpleNumbers[i]==b):
                bc=i
        self.simpleNumbers[ac],self.simpleNumbers[bc]=self.simpleNumbers[bc],self.simpleNumbers[ac]
        self.conceptOct=self.simpleNumbers[0]
    def end(self,end):
        name=end.split(":")[1]
        name=name.replace("\n","")
        self.dictionary[name]=self.actualSame
        self.actualSame=""
    def add(self,name,*args,**kwargs):
        self.note_data_production = []
        fix = self.fix
        turn = self.turn
        edo = self.edo
        inst = self.inst
        vel = self.vel
        valOct = self.valOct
        chan = self.chan
        SM = self.SM
        reLen = self.reLen
        getState = self.getState
        setState = self.setState
        noteBind = self.noteBind
        unBind = self.unBind
        scale = self.scale
        setScale = self.setScale
        root=self.root
        oct=self.oct
        setBase = self.setBase
        n=kwargs.get("n",1)
        command=kwargs.get("cm","")
        cof=kwargs.get("cf",1)
        conficent=cof
        if(self.paternList.get(command)!=None):
            command=self.paternList.get(command)
        instruct=command.split("|")
        fronSt=kwargs.get("fromSt",False)
        s=kwargs.get("s",-1)
        if(s!=-1):
            if(s==1):
                fronSt=True
        mline=[]
        if(fronSt):
            mline=re.split(r"[\n;]",name)
        else:
            mline=self.dictionary.get(name).split("\n")
        for i in range(len(mline)):
            if(mline[i]==""):
                continue
            if(mline[i][0]=="#"):
                continue
            ser=re.search(r'^[ \t]*p',mline[i][0])
            if(ser):
              #  setLen(mline[i][ser.start()+1:].replace(" "))
                self.setLen(re.sub(r'[ \t]','',mline[i][ser.start()+1:]))
            if("SM" in mline[i].split("(")[0].replace(" ","")):
                eval(mline[i])
            if(mline[i].split("(")[0].replace(" ","") in self.simplCom):
                eval(mline[i])
            ser=re.search(r'^[ \t]*n',mline[i][0])
            if(ser):
                l=re.split("[ \t]",mline[i][ser.start()+1:])
                for k in range(len(l)):
                    if(l[k]!=""):
                        self.addNoteCh(l[k])
        if(command!=""):
            for c in instruct:
                if(c!=""):
                    eval(c)
        n-=1
        if(n>0):
            self.add(name,n=n,cm=command)
        else:
            self.conficent=1
        return self.note_data_production
    def commandInter(self,com):
        comm=com
        if(self.paternList.get(com)!=None):
            comm=self.paternList.get(com)
        instruct=comm.split("|")
        if(comm!=""):
            for c in instruct:
                if(c!=""):
                    eval(c)
    def addNoteCh(self,lk):
        ppq = []
        API = "`" in lk
        lkk = lk.split("`")
        if API:
            ppq = eval(lkk[1])
        if("*" in lk):
            self.addChord(lkk[0], API = API, ppq = ppq)
        else:
            self.addNote(lkk[0], API = API, ppq = ppq)
    def addChord(self,lk,**kwargs):
        API = kwargs.get("API",False)
        ppq = kwargs.get("ppq",[])
        mass=kwargs.get("mass",[])
        isCh=kwargs.get("isCh",0)
        chO=lk.split("*")
        if("$$" in chO[1]):
            lst=chO[1].split("$$")
            self.addArp(lst[1],lst[0],chO[0], API = API, ppq = ppq)
            return
        if(chO[1][0]=="("):
            lkk=chO[1].replace("(","")
            lkk=lkk.replace(")","")
            chor=lkk.split(",")
            lEdo=self.EDO
            octCh=self.conceptOct
        else:
            chor=self.dictChords.get(chO[1],{})
            kwargs=self.chKwargs.get(chO[1],{})
            lEdo=kwargs.get("edo",self.EDO)
            octCh=kwargs.get("oct",self.conceptOct)
        se=self.EDO
        so=self.conceptOct
        self.edo(lEdo)
        self.valOct(octCh)
        for i in range(len(chor)):
            self.addNote(chor[i],pose=chO[0],chord=True, API = API, ppq = ppq)
            self.chan()
        self.edo(se)
        self.valOct(so)
        self.timeInBeats+=self.currentLen*self.conficent
        if(self.changeVel):
            self.changeVel=False
            self.veloc=self.lastVel
        if(self.changeLen):
            self.changeLen=False
            self.currentLen=self.LastLen
        if(self.changeOct):
            self.changeOct=False
            self.octave=self.lastOct
    def addArp(self,arpName,chordName,rootNote,**kwargs):
        API = kwargs.get("API", False)
        ppq = kwargs.get("ppq", [])
        temp=self.currentTemp
        templ=self.tempP
        cof=self.conficent
        coef=1
        name=arpName
        if(">" in arpName):
            coef=eval(arpName.split(">")[1])
            name=arpName.split(">")[0]
        self.conficent=coef*self.conficent
        self.setScale(chordName,ch=1)
        arp=self.arpegDict.get(name)
        for a in arp:
            if a[0]=="(":
                stra=rootNote+"*"+a
                self.addChord(stra, API = API, ppq = ppq)
            else:
                self.addNote(a,pose=rootNote, API = API, ppq = ppq)
        self.conficent=cof
        self.currentTemp=temp
        self.tempP=templ

    def sum_pitch(self,rootm,pose,note,conceptOct,octave):
        nOne = self.fcent(rootm) + self.fcent(pose) + self.fcent(note) + self.cents(conceptOct) * octave
        return self.midipith(nOne)

    def alls_pitch(self, note):
        return self.fcent(note) * 4096 / 100
    def allfix(self):
        self.fix()
        self.getState()
    def allturn(self):
        self.turn()
        self.setState()
    def addNote(self,lk,*args,**kwargs):
        API = kwargs.get("API", False)
        ppq = kwargs.get("ppq", [])
        chaneL=kwargs.get('chanel',self.GlobalChanel)
        pose=kwargs.get('pose',"0")
        choRR=kwargs.get('chord',False)
        count=kwargs.get('count',1)
        if self.Binded:
            self.commandInter(self.bindPattern)
        if(self.Random):
            self.inst(-1)
        chaneL=chaneL%self.chanMax
        if(chaneL==9):
            self.chan()
            chaneL=(chaneL+1)%self.chanMax
        #nOne=self.fcent(self.rootm)+self.fcent(pose)+self.fcent(lk)+self.cents(self.conceptOct)*self.octave
        nRoot=self.sum_pitch(self.rootm,pose,lk,self.conceptOct,self.octave)
       
        a = self.currentLen+1
        LocLen=self.currentLen
        if(self.dLongBoll):
            LocLen=self.dLong

        timeInBeats2 = self.timeInBeats
        LocLen2 = LocLen
        if API:
            timeInBeats2 = ppq[0]/960
            LocLen2 = ppq[1]/960
        LocLen2 = LocLen2*self.conficent
        if(not self.pause):
            if not False:
                if self.reapyBol:
                    addReapy.addReapy2(self.take, self.note + nRoot[0], int(self.toPith(nRoot[1])), chaneL, timeInBeats2 * 960, LocLen2 * 960, self.veloc, lk)
                self.midi.addNote(0,chaneL,self.note+nRoot[0],timeInBeats2,LocLen2,self.veloc)
                self.midi.addPitchWheelEvent(0,chaneL,timeInBeats2,int(self.toPith(nRoot[1])))
                self.MyMIDI.addNote(self.track,chaneL,self.note+nRoot[0],timeInBeats2,LocLen2,self.veloc)
                self.MyMIDI.addPitchWheelEvent(self.track,chaneL,timeInBeats2,int(self.toPith(nRoot[1])))
            else:
                self.note_data_production.append(note_prod(self.note+nRoot[0],int(self.toPith(nRoot[1])),toppx(timeInBeats2),toppx(LocLen2),self.veloc,lk))
        self.TextVis+=self.rootm+";"+lk+";"+str(timeInBeats2)+";"+str(LocLen2)+";"+str(chaneL)+";"+str(self.EDO)+";"+pose+"\n"
        if(self.dLongBoll):
            self.chan()
            self.dLongBoll=False
        self.MyMIDI.addProgramChange(self.track,chaneL,self.timeInBeats,self.instr)
        self.midi.addProgramChange(0,chaneL,self.timeInBeats,self.instr)
        self.pause =False
        if(not choRR):
            self.timeInBeats+=self.currentLen*self.conficent
            if(self.changeVel):
                self.changeVel=False
                self.veloc=self.lastVel
            if(self.changeLen):
                self.changeLen=False
                self.currentLen=self.LastLen
            if(self.changeOct):
                self.changeOct=False
                self.octave=self.lastOct
    def APIadd(self,time,length,vel,note):
        self.timeInBeats=time
    # automatically)
    def evalContex(self,inp):
        addNote = self.addNote
        load = self.load
        fix = self.fix
        turn = self.turn
        edo = self.edo
        inst = self.inst
        vel = self.vel
        valOct = self.valOct
        chan = self.chan
        SM = self.SM
        reLen = self.reLen
        getState = self.getState
        setState = self.setState
        noteBind = self.noteBind
        unBind = self.unBind
        setScale = self.setScale
        swap = self.swap
        tp = self.tp
        root = self.root
        oct = self.oct
        arpeg = self.arpeg
        chord = self.chord
        pattern = self.pattern
        scale = self.scale
        add = self.add
        setBase = self.setBase
        eval(self.convertNormal(inp))
    def OneStep(self,mus,i,**kwargs):
        text = kwargs.get("text",mus[i])
        pk = text.replace("\n", "")
        if (pk.replace(" ", "").replace("\t", "") == "pyGloabal"):
            self.GlobalPy = True
            self.Py = True
            return
        if (pk.split(":")[0].replace(" ", "").replace("\t", "") == "pyLocal"):
            if (len(text.split(":")) > 1):
                self.pyArg = int(text.split(":")[1].replace(" ", ""))
            self.GlobalPy = False
            self.Py = True
            return
        if (not self.Py):
            spl = pk.split(";")
            for j in range(len(spl)):
                if (pk == ""):
                    continue
                if (spl[j] == ""):
                    continue
                if (pk[0] == "#"):
                    continue
                if ("same" == spl[j].replace(" ", "").replace("\t", "")):
                    self.sameB = True
                    continue
                # print(mus[i][0:2])
                if ("end" == spl[j].split(":")[0].replace(" ", "").replace("\t", "")):
                    self.sameB = False
                    self.end(spl[j])
                    self.actualSame = ""
                    continue
                if (not self.sameB):
                    #   print(spl[j])
                    self.evalContex(spl[j])
                else:
                    self.same(self.convertNormal(spl[j]))
        else:
            if (text.replace(" ", "") == "endPy"):
                if (self.GlobalPy):
                    self.pyContext(self.localPy)
                    self.GlobalPy = False
                else:
                    if (self.pyArg == 1):
                        self.pythonEval(self.localPy, var=True)
                    else:
                        self.pythonEval(self.localPy)
                self.localPy = ""
                self.Py = False
            else:
                self.localPy += text + "\n"

    def startAll(self):
        for i in range(self.line,len(self.mus)):
           
            self.OneStep(self.mus,i)

    def output(self):
        if(not self.fromStr):
            Path(self.namefile.replace(self.namefile.split("/")[len(self.namefile.split("/"))-1],"visual/")).mkdir(parents=True, exist_ok=True)
            with open(self.namefile.replace(self.namefile.split("/")[len(self.namefile.split("/"))-1],"visual/"+self.namefile.split("/")[len(self.namefile.split("/"))-1]).replace(".muz",".vis"), "w") as f:
                f.write(self.TextVis)
            p=self.namefile.replace(self.namefile.split("/")[len(self.namefile.split("/"))-1],"midi/")
            Path(self.namefile.replace(self.namefile.split("/")[len(self.namefile.split("/"))-1],"midi/")).mkdir(parents=True, exist_ok=True)
            with open(self.namefile.replace(self.namefile.split("/")[len(self.namefile.split("/"))-1],"midi/"+self.namefile.split("/")[len(self.namefile.split("/"))-1]).replace(".muz",".mid"),"wb") as output_file:
                self.midi.writeFile(output_file)
        else:
            with open(self.namefile+".mid","wb") as output_file:
                self.midi.writeFile(output_file)
        return True

