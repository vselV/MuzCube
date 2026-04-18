import random
from src.MuzCube.Scripts import addReapy
from midiutil import MIDIFile
import math
from pathlib import Path
import re
class toMidi():
    def __init__(self,namefile,track,MyMIDI,**kwargs):
        self.namefile = namefile
        self.track = track
        self.midi =MIDIFile(1)
        self.pohu=kwargs.get("pohu",False)

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
        self.simplCom=["oct","inst","root","fix","turn","edo","valOct","chan","vel","getState","setState"]
        self.stateMent=["rootm","currentLen","octave","instr","veloc","EDO","EDOconst","GlobalChanel","timePoint"]

        self.pythonKeyWords = ["pyGlobal","pyLocal","endPy"]

        self.noSCOB = ["fix","turn","getState","setState","unBind"]
        self.withArg = ["vel","root","chan","reLen","setScale","edo","oct","valOct"]
        self.withArgNotStr = ["chan","tp","edo","oct","valOct"]
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

        if(not self.fromStr):
            self.file = open(self.namefile, 'r')
            self.mus =self.file.readlines()
        else:
            self.mus= self.lineStr.split("\n")
        self.tempo=120
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
        self.MyMIDI.addTrackName(track, 0, self.namefile)
        self.midi.addTrackName(0, 0, self.namefile)
        self.GlobalPy = False
        self.Py = False
        self.pyArg = 0
        self.localPy = ""
    def convertNormal(self,command):
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
                print(name + "('"+sp[1]+"', s=1)")
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
    def pythonEval(self,StrCode,**kwargs):
        nonlocal root,oct,inst,vel,edo,valOct,chan,reLen,setScale
        nonlocal load,swap,chord,pattern,scale,arpeg
        nonlocal fix,turn,tp,getState,setState,unBind,noteBind
        nonlocal addNote
        if(kwargs.get("var",False)):
            nonlocal veloc,rootm,octave,edo,currentLen,timeInBeats,conceptOct,timePoint
            eval(self.GlobalPythonContext+StrCode)
        else:
            eval(self.GlobalPythonContext+StrCode)
    def setDeaf(self):
        nonlocal dictionary,dictChords,TempDict,chKwargs,tempKwargs,paternList
        self.vel(80)
        self.edo(12)

    def valOct(self,nOct):
        nonlocal conceptOct
        conceptOct=nOct
    def inst(self,p):
        nonlocal instr, Random
        if type(p) is int:
            instr=p
        if type(p) is str:
            if(p=="rand"):
                Random=not Random
        if(Random and p==-1):
            instr=random.randint(0, 127)
    def chord(self,name,mass,*args,**kwargs):
        nonlocal dictChords,chKwargs
        chKwargs[name]=kwargs
      #  lEdo=kwargs.get("edo",-1)
      #  octCh=kwargs.get("oct",-1)
        if type(mass) is list:
            dictChords[name]=mass
        if type(mass) is str:
            dictChords[name]=mass.split(" ")
    def chan(self,*args):
        nonlocal GlobalChanel
        if(len(args)==0):
            GlobalChanel+=1
        else:
            GlobalChanel=args[0]
    def fix(self):
        nonlocal timePoint
        timePoint=self.timeInBeats
    def turn(self):
        nonlocal timeInBeats
        timeInBeats=timePoint
    def setDl(self):
        nonlocal dLong,dLongBoll
    def loadEval(self,aS,mus):
        nonlocal chord,pattern,scale
        if(aS!=""):
            mSp=re.split(r"\( *",mus,1)
            simb=mSp[1][0]
            stroc=mSp[0]+"("+simb+aS+"."+mSp[1][1:]
            eval(stroc)
        else:
            eval(mus)
    def load(self,file,**kwargs):
        nonlocal chord,pattern,scale
        aS=kwargs.get("as","")
        ro=kwargs.get("root",0)
        sk=False
        lod=namefile.split("/")
        dir=""
        for i in range(len(lod)-1):
            dir+=lod[i]
        nf=dir+"/"+file
        if(ro==1):
            nf=file
        h=open(nf,"r")
        mus=h.readlines()
        for i in range(len(mus)):
            print(sameB)
            pk=mus[i].replace("\n","")
            spl=mus[i].split(";")
            for j in range(len(spl)):
                if("chord" in spl[j].split("(")[0]):
                    loadEval(aS,mus[i])
                if("pattern" in spl[j].split("(")[0]):
                    loadEval(aS,spl[j])
                if("scale" in spl[j].split("(")[0]):
                    loadEval(aS,spl[j])
                if("arpeg" in spl[j].split("(")[0]):
                    loadEval(aS,spl[j])
                if(pk==""):
                    continue
                if("same" == spl[j].replace(" ","")):
                    sk=True
                    continue
                if("end" == spl[j].split(":")[0].replace(" ","")):
                    sk=False
                    end(mus[i])
                    continue
                if(sk):
                    same(mus[i])
        h.close()
    def oct(self,o,*args,**kwargs):
        nonlocal octave,lastOct,changeOct
        last=kwargs.get("last",False)
        char=kwargs.get("char","")
        if(last):
            changeOct=True
            lastOct=octave
            if(o==""):
                octave=octave+int(char+"1")
            else:
                octave=octave+int(char+o)
        else:
            if(type(o) is str):
                k=eval("octave"+o)
                octave=k
            else:
                octave=o
        print(octave)
    def notSpec(self,note):
        for c in special:
            if c in note:
                return False
        return True
    def root(self,r):
        nonlocal rootm
        if(r[0]=="~"):
            dtr=r[1:]
            if(notSpec(dtr) and notSpec(rootm)):

                #print(dtr)
                nm1=dtr.split(".")
                nm2=rootm.split(".")
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
                rootm=strK
            else:
                rootm=str(fcent(rootm)+fcent(dtr))+"c"
        else:
            rootm=r
    def tp(self,time):
        nonlocal timeInBeats
        timeInBeats=time
    def same(self,l):
       # print(l)
        nonlocal actualSame
        actualSame+=l+"\n"
    def vel(self,v,*args,**kwargs):
        nonlocal veloc,lastVel,changeVel
        last=kwargs.get("last",False)
        if type(v) is str:
            p=eval("veloc"+v)
            veloc=min(127,p)
            veloc=max(0,veloc)
            print(veloc)
            return
        if(last):
            lastVel=veloc
            changeVel=True
            veloc=v
        else:
            veloc=v
    # print(actualSame)
    def reLen(self,com):
        nonlocal currentLen
        if type(com) is str:
            p=eval("currentLen"+com)
            currentLen=p
            return
        else:
            currentLen=com
    def getNum(self,nump):
        nonlocal pause
        if nump=="_":
            pause=True
            return 1
        m=nump.split(".")
        intA=1
        for i in range(len(m)):
            intA=intA*math.pow(simpleNumbers[FromI+i],int(m[i]))
        return intA
    def edo(self,edo):
        nonlocal EDO,EDOconst
        EDO=edo
        EDOconst=math.pow(conceptOct,1/EDO)
    def tPose(self,num):
        j=num
      #  p=tPoseRot(getNum(rootm))
        while(j>conceptOct):
            j=j/conceptOct
        while(j<1):
            j=j*conceptOct
        return j
    def pattern(self,name,patern):
        nonlocal paternList
        paternList[name]=patern
    def tPoseRot(self,rootm):
        j=rootm
        while(j>conceptOct):
            j=j/conceptOct
        while(j<1):
            j=j*conceptOct
        return j
    def scale(self,name,strk,**kwargs):
        nonlocal TempDict,tempKwargs
        sort=kwargs.get("sort",0)
        tem=[]
        if strk is str:
            tem=strk.split(" ")
        else:
            tem=strk
        ftem=[]
        cents = []
        getState()
        for st in tem:
            if st != "":
                cents.append(fcentOct(st))
                ftem.append(st)
        if sort==1:
            ftem=SortTwo(cents,ftem)
        setState()
        TempDict[name]=ftem
        tempKwargs[name]=kwargs
    def fromTmp(self,index,name,**kwargs):
        nonlocal EDO,conceptOct
       # ch=kwargs.get("ch",0)
        if(not tempP):
            mass=dictChords.get(name)
            arg=chKwargs.get(name)
            edos=arg.get("edo",12)
            octS=arg.get("oct",2)
        else:
            mass=TempDict.get(name)
            arg=tempKwargs.get(name)
            edos=arg.get("edo",12)
            octS=arg.get("oct",2)
        a=conceptOct
        b=EDO
        edo(edos)
        setOct(octS)
        m=fcentOct(mass[index%(len(mass))])
        octCh=index//(len(mass))
        edo(a)
        setOct(b)
        return m+octCh*int(math.log(octS,oneCent))
    def SortTwo(self,base,obj):
        dictL={}
        mp=[]
        for i in range(len(base)):
            dictL[base[i]]=obj
        sort=sorted(base)
        for i in range(len(base)):
            mp.append(dictL.get(sort[i]))
        return mp
    def noteBind(self,patternName,**kwargs):
        nonlocal bindPattern,Binded
        bindPattern=patternName
        Binded=True
    def unBind(self):
        Binded=False
    def setOct(self,num):
        return num*math.pow(conceptOct,octave)
    def cents(self,num):
        return math.log(num,oneCent)
    def midipith(self,cents):
        return [int(cents)//100,int(cents)%100+(cents-math.floor(cents))]
    def toPith(self,cnt):
        return 8192/200*cnt
    def fromEdo(self,step):
        return math.pow(EDOconst,step)
    def inOne(self,mass,str):
        for k in mass:
            if k in str:
                return True
        return False
    def fcent2(self,fc):
        if "f" in fc:
            return cents(float(fc.replace("f","")))
        if "c" in fc:
            return int(fc.replace("c",""))
        if "с" in fc:
            return int(fc.replace("с",""))
        if "e" in fc:
            return cents(fromEdo(float(fc.replace("e",""))))
        return cents(setOct(tPose(getNum(fc))))
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
        interPr(fc[ct:])
     #   print(fc)
       # print(str)
        return fcentOct(str)
    def SM(self,name,**kwargs):
        cnt=kwargs.get("n",1)
        com=kwargs.get("cm","")
        st=kwargs.get("st",0)
        cf=kwargs.get("cf",1)
        if(st==1):
            getState()
        if(name[0]==":"):
            add(name[1:],n=cnt,cm=com,fromSt=True,cf=cf)
        else:
            add(name,n=cnt,cm=com,cf=cf)
        if(st==1):
            setState()
    def fcentOct(self,fc):
        if "f" in fc:
            return cents(eval(fc.replace("f","").replace("x","*")))
        if "c" in fc:
            return int(fc.replace("c",""))
        if "с" in fc:
            return int(fc.replace("с",""))
        if "e" in fc:
            return cents(fromEdo(float(fc.replace("e",""))))
        if "t" in fc:
            return fromTmp(int(fc.replace("t","")),currentTemp)
        return cents(tPose(getNum(fc)))
    def setScale(self,name,**kwargs):
        nonlocal currentTemp,tempP
        ch=kwargs.get("ch",0)
        if(ch==1):
            tempP=False
        else:
            tempP=True
        currentTemp=name
    def arpeg(self,name,listp):
        nonlocal arpegDict
        if type(listp) is list:
            arpegDict[name]=listp
        if type(listp) is str:
            arpegDict[name]=listp.split(" ")
    def interA(self,strK,p):
        if(p==":"):
            setLen(strK,last=True)
        if(p=="+" or p=="-"):
            oct(strK,last=True,char=p)
        if(p=="v"):
            vel(strK,last=True)
        if(p=="="):
            setLen(strK,dLong=True)
    def interPr(self,lin):
        strK=""
        p=""
        for k in lin:
          #  print(k)
            if k in separateMass:
                if(p!=""):
                    interA(strK,p)
                strK=""
                p=k
            else:
                if p != "":
                    strK+=k
        if(p!=""):
            interA(strK,p)
    def setLen(self,h,*args,**kwargs):
        nonlocal currentLen,LastLen,currentLen,changeLen,dLong,dLongBoll
        last=kwargs.get("last",False)
        dLongL=kwargs.get("dLong",False)
        if(last):
            LastLen=currentLen
            changeLen=True
        l1="."in h
        l2=".."in h
        t=h.replace(".","").split("t")
        if(dLongL):
            dLong=dictionaryVal.get(t[0])
            dLongBoll=True

        lenm=dictionaryVal.get(t[0])
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
            dLong=lenm
            dLongBoll=True
        else:
            currentLen=lenm
        print(currentLen)
    def getState(self):
        nonlocal state
        state=[rootm,currentLen,octave,instr,veloc,EDO,EDOconst,GlobalChanel,timePoint]
    def setState(self):
        nonlocal rootm,currentLen,octave,instr,veloc,EDO,EDOconst,GlobalChanel,timePoint
        print(state)
        rootm,currentLen,octave,instr,veloc,EDO,EDOconst,GlobalChanel,timePoint=state
        print([rootm,currentLen,octave,instr,veloc,EDO,EDOconst,GlobalChanel,timePoint])
        #for i in range(len(state)):
         #   exec(stateMent[i]+"="+str(state[i]))
    def swap(self,*args):
        nonlocal simpleNumbers,conceptOct
        if(len(args)==0):
            simpleNumbers=[2,3,5,7,11,13,17,19,23]
            conceptOct=2
            return
        a=args[0]
        b=args[1]
        ac=0
        bc=0
        for i in range(len(simpleNumbers)):
            if(simpleNumbers[i]==a):
                ac=i
            if(simpleNumbers[i]==b):
                bc=i
        simpleNumbers[ac],simpleNumbers[bc]=simpleNumbers[bc],simpleNumbers[ac]
        conceptOct=simpleNumbers[0]
    def end(self,end):
        nonlocal actualSame
        name=end.split(":")[1]
        name=name.replace("\n","")
     #   print(name)
       # print(name)
        dictionary[name]=actualSame
        actualSame=""
    def add(self,name,*args,**kwargs):
        nonlocal timeInBeats,conficent,arpeg
        nonlocal pause,fix,turn,edo,inst,vel,valOct,chan,SM,reLen,getState,setState,noteBind,unBind,scale,setScale
        nonlocal TextVis,changeVel,changeOct,changeLen,LastLen,lastOct,lastVel,veloc,currentLen,octave,root,oct
        n=kwargs.get("n",1)
        command=kwargs.get("cm","")
        cof=kwargs.get("cf",1)
        conficent=cof
        if(paternList.get(command)!=None):
            command=paternList.get(command)
        instruct=command.split("|")
        fronSt=kwargs.get("fromSt",False)
        s=kwargs.get("s",-1)
        if(s!=-1):
            if(s==1):
                fronSt=True
      #  print(dictionary.get(name),"++++")
        print(name)
        mline=[]
        if(fronSt):
            mline=re.split(r"[\n;]",name)
        else:
            mline=dictionary.get(name).split("\n")
        for i in range(len(mline)):
            if(mline[i]==""):
                continue
            if(mline[i][0]=="#"):
                continue
            ser=re.search(r'^[ \t]*p',mline[i][0])
            if(ser):
              #  setLen(mline[i][ser.start()+1:].replace(" "))
                setLen(re.sub(r'[ \t]','',mline[i][ser.start()+1:]))
            if("SM" in mline[i].split("(")[0].replace(" ","")):
                eval(mline[i])
            if(mline[i].split("(")[0].replace(" ","") in simplCom):
                eval(mline[i])
           # print(mline)
            ser=re.search(r'^[ \t]*n',mline[i][0])
            if(ser):
              #  l=mline[i][ser.start()+1:].split(" ")
                l=re.split("[ \t]",mline[i][ser.start()+1:])
                for k in range(len(l)):
                    if(l[k]!=""):
                        addNoteCh(l[k])

                    #MyMIDI.addPitchWheelEvent(0,0,timeInBeats,int(toPith(nRoot[1])))
        if(command!=""):
            for c in instruct:
                if(c!=""):
                    eval(c)
        n-=1
        if(n>0):
            add(name,n=n,cm=command)
        else:
            conficent=1
    def commandInter(self,com):
        comm=com
        if(paternList.get(com)!=None):
            comm=paternList.get(com)
        instruct=comm.split("|")
        if(comm!=""):
            for c in instruct:
                if(c!=""):
                    eval(c)
    def addNoteCh(self,lk):
        if("*" in lk):
            addChord(lk)
        else:
            addNote(lk)
    def addChord(self,lk,**kwargs):
        nonlocal timeInBeats,chKwargs,dictChords,changeVel,changeVel,changeVel,changeLen,changeOct,veloc,octave,currentLen
        mass=kwargs.get("mass",[])
        isCh=kwargs.get("isCh",0)
        chO=lk.split("*")
        if("$$" in chO[1]):
            lst=chO[1].split("$$")
            addArp(lst[1],lst[0],chO[0])
            return
        if(chO[1][0]=="("):
            lkk=chO[1].replace("(","")
            lkk=lkk.replace(")","")
            chor=lkk.split(",")
            lEdo=EDO
            octCh=conceptOct
        else:
            chor=dictChords.get(chO[1],{})
            kwargs=chKwargs.get(chO[1],{})
            lEdo=kwargs.get("edo",EDO)
            octCh=kwargs.get("oct",conceptOct)
        se=EDO
        so=conceptOct
        edo(lEdo)
        valOct(octCh)
        for i in range(len(chor)):
            addNote(chor[i],pose=chO[0],chord=True)
            chan()
        edo(se)
        valOct(so)
        timeInBeats+=currentLen*conficent
        if(changeVel):
            changeVel=False
            veloc=lastVel
        if(changeLen):
            changeLen=False
            currentLen=LastLen
        if(changeOct):
            changeOct=False
            octave=lastOct
    def addArp(self,arpName,chordName,rootNote):
        nonlocal tempP,currentTemp,conficent
        temp=currentTemp
        templ=tempP
        cof=conficent
        coef=1
        name=arpName
        if(">" in arpName):
            coef=eval(arpName.split(">")[1])
            name=arpName.split(">")[0]
        conficent=coef*conficent
        setScale(chordName,ch=1)
        print(arpegDict)
        print(name)
        arp=arpegDict.get(name)
        print(arp)
        for a in arp:
            if a[0]=="(":
                stra=rootNote+"*"+a
                addChord(stra)
            else:
                addNote(a,pose=rootNote)
        conficent=cof
        currentTemp=temp
        tempP=templ
    def addNote(self,lk,*args,**kwargs):
        nonlocal timeInBeats
        nonlocal pause,dLong,dLongBoll
        nonlocal TextVis,changeVel,changeOct,changeLen,LastLen,lastOct,lastVel,veloc,currentLen,octave,root,oct
        chaneL=kwargs.get('chanel',GlobalChanel)
        pose=kwargs.get('pose',"0")
        choRR=kwargs.get('chord',False)
        count=kwargs.get('count',1)
        if Binded:
            commandInter(bindPattern)
        if(Random):
            inst(-1)
        chaneL=chaneL%16
        if(chaneL==9):
            chan()
            chaneL=(chaneL+1)%16
        nOne=fcent(rootm)+fcent(pose)+fcent(lk)+cents(conceptOct)*octave
        nRoot=midipith(nOne)
        #   print(nOne,nRoot[0],timeInBeats,currentLen)
      #  print(note+nRoot[0])
        LocLen=currentLen
        if(dLongBoll):
            LocLen=dLong
        if(not pause):
            if reapyBol:
                addReapy.addReapy(take, note + nRoot[0], int(toPith(nRoot[1])), chaneL, timeInBeats, LocLen * conficent, veloc)
            midi.addNote(0,chaneL,note+nRoot[0],timeInBeats,LocLen*conficent,veloc)
            midi.addPitchWheelEvent(0,chaneL,timeInBeats,int(toPith(nRoot[1])))
            MyMIDI.addNote(track,chaneL,note+nRoot[0],timeInBeats,LocLen*conficent,veloc)
            MyMIDI.addPitchWheelEvent(track,chaneL,timeInBeats,int(toPith(nRoot[1])))
        TextVis+=rootm+";"+lk+";"+str(timeInBeats)+";"+str(currentLen*conficent)+";"+str(chaneL)+";"+str(EDO)+";"+pose+"\n"
        if(dLongBoll):
            chan()
            dLongBoll=False
        MyMIDI.addProgramChange(track,chaneL,timeInBeats,instr)
        midi.addProgramChange(0,chaneL,timeInBeats,instr)
        pause =False
        if(not choRR):
            timeInBeats+=currentLen*conficent
            if(changeVel):
                changeVel=False
                veloc=lastVel
            if(changeLen):
                changeLen=False
                currentLen=LastLen
            if(changeOct):
                changeOct=False
                octave=lastOct
    def APIadd(self,time,length,vel,note):
        timeInBeats=time
    # automatically)
    def OneStep(self,i):
        pk = mus[i].replace("\n", "")
        if (pk.replace(" ", "").replace("\t", "") == "pyGloabal"):
            GlobalPy = True
            Py = True
            return
        if (pk.split(":")[0].replace(" ", "").replace("\t", "") == "pyLocal"):
            if (len(mus[i].split(":")) > 1):
                pyArg = int(mus[i].split(":")[1].replace(" ", ""))
            GlobalPy = False
            Py = True
            return
        if (not Py):
            spl = pk.split(";")
            for j in range(len(spl)):
                if (pk == ""):
                    continue
                if (spl[j] == ""):
                    continue
                print(spl[j], sameB)
                if (pk[0] == "#"):
                    continue
                # print(mus[i][0:3])

                if ("same" == spl[j].replace(" ", "").replace("\t", "")):
                    sameB = True
                    continue
                # print(mus[i][0:2])
                if ("end" == spl[j].split(":")[0].replace(" ", "").replace("\t", "")):
                    sameB = False
                    end(spl[j])
                    actualSame = ""
                    continue
                if (not sameB):
                    #   print(spl[j])
                    eval(convertNormal(spl[j]))
                else:
                    same(convertNormal(spl[j]))
        else:
            if (mus[i].replace(" ", "") == "endPy"):
                if (GlobalPy):
                    pyContext(localPy)
                    GlobalPy = False
                else:
                    if (pyArg == 1):
                        pythonEval(localPy, var=True)
                    else:
                        pythonEval(localPy)
                localPy = ""
                Py = False
            else:
                localPy += mus[i] + "\n"

    def startAll(self):
        for i in range(line,len(mus)):
            self.OneStep(i)

    def output(self):
        if(not fromStr):
            Path(self.namefile.replace(namefile.split("/")[len(namefile.split("/"))-1],"visual/")).mkdir(parents=True, exist_ok=True)
            with open(namefile.replace(namefile.split("/")[len(namefile.split("/"))-1],"visual/"+namefile.split("/")[len(namefile.split("/"))-1]).replace(".txt","(visual).txt"), "w") as f:
                f.write(TextVis)
            p=namefile.replace(namefile.split("/")[len(namefile.split("/"))-1],"midi/")
            Path(namefile.replace(namefile.split("/")[len(namefile.split("/"))-1],"midi/")).mkdir(parents=True, exist_ok=True)
            print(namefile.replace(namefile.split("/")[len(namefile.split("/"))-1],"midi/"+namefile.split("/")[len(namefile.split("/"))-1]).replace(".txt",".mid"))
            with open(namefile.replace(namefile.split("/")[len(namefile.split("/"))-1],"midi/"+namefile.split("/")[len(namefile.split("/"))-1]).replace(".txt",".mid"),"wb") as output_file:
                self.midi.writeFile(output_file)
        else:
            with open(namefile+".mid","wb") as output_file:
                self.midi.writeFile(output_file)
        return True