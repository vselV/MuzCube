import math
import pyautogui
import tkinter as tk
from tkinter import ttk, simpledialog
from tkinter import *
from Scripts import toMidiMeth, toMidGa
from midiutil import MIDIFile
import threading
import re
import keyboard
import time
import src.MuzCube.FirstVersion.PlayOneNote
import ch
import src.MuzCube.UtilMath.mathD
class Graph:
    def __init__(self,root,*args, **kwargs):
        pyautogui.FAILSAFE=False
        self.allFrame = ttk.Frame( relief=SOLID, padding=[8, 10])
        self.FrameStats=ttk.Frame(self.allFrame)

        self.array=kwargs.get('array', [])
        self.arrayRate=0.02
        self.EnabeLines=False

        self.defDir=[3,5,7,11,13,17,19]
        self.dirCnt=3
        self.colorConfig=["#994242","#699942","#42528a","#654299","#429998","#997642"]
        self.conceptOctave=kwargs.get('conceptOctave', 2)
        #fly
        self.path=kwargs.get('path', "")
        self.file=kwargs.get('file', "")
        self.Range=2
        #листы
        self.buttonList=[]


        self.directions=kwargs.get('directions', self.defDir)
        self.axsis=kwargs.get('axsis', False)
        self.winStats=kwargs.get('winStats',"800x800+300+300")
        self.mouseBlock=kwargs.get('mouseBlock',True)
        self.keyBlock=kwargs.get('mouseBlock',True)
        self.kfSize=kwargs.get('kfSize',2)
        self.cursorColor=kwargs.get('cursorColor',"#000000")
        self.cursorText=kwargs.get('cursorText',"+")
        self.intst=kwargs.get('inst',0)
        self.configVect=kwargs.get('configVect',"configVectors")
        self.CONF=ch.readConfig(self.configVect)
        self.rePointRate=kwargs.get('rePointRate',0.1 )
        self.dictFromOval={}
        self.dirCount=3
        self.inScreenDots=[]
        self.DotsChord=[]

        self.mousepose = pyautogui.position()

        self.VectXY =[0,0]
        self.VectView = [0,0,1]
        self.PoseChords = [0.5,0.5,-5]
        self.intPoseK=[0,0,0]
        ##
        self.ObjPose=[0,0,0]
        self.poseObjVect=[0,0,0]
        self.recrateBool=False
        ##
        self.lastpose=[0,0,0]

        self.framerate=50
        filesPlay=["file."]


        self.splitStats = re.split("\\+|x",self.winStats)
        self.intStats=[int(self.splitStats[0]),int(self.splitStats[1]),int(self.splitStats[2]),int(self.splitStats[3])]
        self.size=[self.intStats[0],self.intStats[1]]

        self.MasterLines=""

        self.ovalCnt=0
        self.ovals=[]
        self.words=[]

        self.curentMassOval=[]
        self.massOvalChords=[]
        self.OvalTag=""
        self.select=''
        self.massOval=False
        self.dopOv=False
        self.dvOv=False

        self.octave=0
        self.conLen="#"
        self.curLen="#"
        self.conVel=80

        self.mouseSens=0.002

        self.noFrameRate=40

        self.step=0.10
        self.wk=False
        self.ak=False
        self.sk=False
        self.dk=False
        #play
        self.tempo=kwargs.get('tempo',120)
        self.times=kwargs.get('time',1)
        self.programm=kwargs.get('programm',1)
        self.midinote=kwargs.get('midinote',60)
        self.oct=kwargs.get('oct',0)
        self.vel=kwargs.get('vel',80)
        self.rootNote=kwargs.get('rootNote',"0")
        self.simpleNumbers=kwargs.get('simpleNumbers',[2,3,5,7,11,13,17,19,23])
        self.dictObj={}
        self.objList2=[]

        self.focused=False

        self.canvas = Canvas(self.allFrame,bg="white", width=int(self.splitStats[0]), height=int(self.splitStats[1]))

        self.cursorPlus=self.canvas.create_text(self.intStats[0]/2-5,self.intStats[1]/2-5,anchor=NW,text=self.cursorText,fill=self.cursorColor,state="hidden",tags=["cursor"])

        self.entry_text = tk.StringVar()
        self.entry = tk.Entry(self.allFrame, textvariable=self.entry_text ,bg="grey87",fg="NavyBlue", width=int(self.size[0]/10))
        self.context_text = tk.StringVar()
        self.context_entry = tk.Entry(self.allFrame, textvariable=self.context_text ,bg="grey87",fg="NavyBlue", width=int(self.size[0]/12))
        self.entry_text.set("n")

        self.checkL = tk.BooleanVar(value=False)
        self.check_lines = ttk.Checkbutton(self.FrameStats,text="Lines", variable=self.checkL)
        self.checkOt=tk.BooleanVar(value=False)
        self.checkOO= ttk.Checkbutton(self.FrameStats,text="Fixed Cube", variable=self.checkOt)

        self.chord=tk.StringVar()
        self.entry_cords=tk.Entry(self.FrameStats, textvariable=self.chord ,bg="grey87",fg="NavyBlue", width=20,state="readonly")
        self.chordObj=tk.StringVar()
        self.entry_Objcords=tk.Entry(self.FrameStats, textvariable=self.chordObj ,bg="grey87",fg="NavyBlue", width=20,state="readonly")

        self.EntryEnabe=False
        #chekboxes
        self.checkEntry = tk.BooleanVar(value=self.EntryEnabe)
        self.EntryBox = ttk.Checkbutton(self.allFrame,text="Rec", variable=self.checkEntry)
        self.entry_cords.pack()
        self.entry_Objcords.pack()
        self.check_lines.pack()
        self.checkOO.pack()

        self.PlayBoll=False
        self.curentFrame=0
        self.AllChanDict={}
        self.maxEv=0
        self.ObjectList = []
        self.objList2=self.ObjectList.copy()

        self.ct=0
        self.kfmove=1
        self.trEd=""

        self.createObjects(self.Range,dir=self.dirCnt,poseChords=[0,0,0])
        self.canvas.bind('<ButtonPress-1>', self.click)
        self.canvas.bind('<Alt-KeyPress-f>', self.changeCurs)
        self.canvas.bind('<Alt-KeyPress-g>', self.enabeWASD)
        self.canvas.bind('<Control-KeyPress-f>', self.DirChange)
        self.canvas.bind('<F1>', self.playEntr)
        self.canvas.bind('<Control-KeyPress-c>', self.copy)
        self.canvas.bind('<KeyPress-h>', self.DirCount)
        self.canvas.bind('<KeyPress-y>', self.rangeDir)
        self.canvas.bind('<KeyPress-q>', self.objectRecreate)
        self.canvas.bind('<KeyPress-m>', self.Manual)
        #canvas.bind('<KeyPress-p>', rgrecrate1)
        #canvas.bind('<KeyPress-p>', startPlayBind)
        self.canvas.bind('<KeyPress-e>', self.Enabe)
        self.canvas.bind('<KeyPress-r>', self.clearEntr)
        self.canvas.bind('<KeyPress-t>', self.tp0)
        self.canvas.bind('<KeyPress-b>', self.backSpace)
        self.canvas.bind('<KeyPress-l>', self.DrewLines)
        self.canvas.bind('<KeyPress-o>', self.rgrecrate1)
        self.canvas.bind('<KeyPress-u>', self.upDateCube)
        self.allFrame.bind('<FocusIn>',self.noteInstEv)
        self.allFrame.bind('<FocusOut>',self.gits)
        self.manual = tk.Label(self.allFrame, text="инструкция - m(маленькая/англ)")
        self.label3 = tk.Label(self.allFrame, text="context")
        self.manual.pack()
        self.canvas.pack(anchor=CENTER)
        self.FrameStats.pack(anchor=E)
        self.context_entry.pack()
        self.label3.pack()
        self.entry.pack()
        self.EntryBox.pack(anchor=CENTER)
        self.movetread =threading.Thread(target=self.move,daemon = True)
        self.arrayTr=threading.Thread(target=self.arrayMonitoring,daemon=True)
        self.sort =threading.Thread(target=self.mnSort,daemon = True)
        self.sort.start()
        self.allFrame.grid(row = 0, column = 11,columnspan=5,rowspan=4)
        self.movetread.start()
        self.arrayTr.start()
    #def setColorData
    def deafObj(self):
        self.createObjects(self.Range,dir=self.dirCnt,poseChords=self.ObjPose)
    def clearSelection(self):
        for o in self.ObjectList:
            o.deSelect()
    def toLockNote(self,chords):
        ans=""
        for j in chords:
            ans+=str(j)+"."
        ans=ans[0:len(ans)-1]
        return ans
    def getNum(self,nump):
        m=nump.split(".")
        intA=[1,1]
        for i in range(len(m)):
            try:
                if(int(m[i])>0):
                    intA[0]=intA[0]*math.pow(self.directions[i],int(m[i]))
            except:
                intA[0]=404
            try:
                if(int(m[i])<0):
                    intA[1]=intA[1]*math.pow(self.directions[i],-int(m[i]))
            except:
                intA[1]=404
        return intA
    def getNumSt(self,nump):
        m=nump.split(".")
        intA=1
        for i in range(len(m)):
            try:
                intA=intA*math.pow(self.directions[i],int(m[i]))
            except:
                intA=404
        return intA
    def tPose(self,num,num2):
        nnum=num
        j=num2
        c1=0;c2=0
        while(j>self.conceptOctave):
            j=j/self.conceptOctave
            nnum[1]=nnum[1]*self.conceptOctave
        while(j<1):
            c2+=1
            j=j*self.conceptOctave
            nnum[0]=nnum[0]*self.conceptOctave
        return [int(nnum[0]),int(nnum[1])]
    def strNum(self,chords):
        if(chords=="?"):
            return chords
        stA=self.toLockNote(chords)
        mNum=self.tPose(self.getNum(stA),self.getNumSt(stA))
        return str(mNum[0])+"/"+str(mNum[1])
    def createObjects(self,ranGe,**kwargs):
        #nonlocal ObjectList,ovals,words,objList2,ObjPose,MasterLines,intPoseK,poseObjVect
        dirCt=kwargs.get("dir",3)
        poseChords=kwargs.get("poseChords",self.PoseChords)
        if(self.MasterLines!=""):
            self.MasterLines.clear()
        locDir=[]
        for i in range(dirCt):
            locDir.append(self.directions[i])
        for ov in self.ovals:
            self.canvas.delete(ov)
        for wd in self.words:
            self.canvas.delete(wd)
        dt=[]
        if(dirCt<len(self.directions)):
            for i in range(dirCt):
                dt.append(self.directions[i])
        else:
            dt=self.directions
        self.ovals=[]
        self.words=[]
        self.ObjectList=[]
        def recurent(iter,ranGe,direct,startChord,massChord,chordList):
            iter+=1
            for i in range(ranGe):
                kl=massChord.copy()
                #  print(startChord,iter-1)
                kl.append(startChord[iter-1]+i-int(ranGe/2))
                if(iter<len(direct)):
                    recurent(iter,ranGe,direct,startChord,kl,chordList)
                else:
                    chordList.append(kl)
        chordList=[]
        intPose=[int(poseChords[0])+1,int(poseChords[1])+1,int(poseChords[2])+1]

        ItDir=min(dirCt,len(self.directions))
        if(ItDir>3):
            for i in range(ItDir-3):
                intPose.append(1)
        self.ObjPose=poseChords.copy()
        recurent(0,ranGe,dt,intPose,[],chordList)
        graph=[]
        def serch(obj,list):
            for o in range(len(list)):
                if obj== list[o]:
                    return o
            return -1
        for c in range(len(chordList)):
            chord=chordList[c]
            vert=[]
            for i in range(len(chord)):
                nchor=chord.copy()
                nchor[i]+=1
                index=serch(nchor,chordList)
                if(index!=-1):
                    vert.append(index)
                nchor[i]-=2
                index=serch(nchor,chordList)
                if(index!=-1):
                    vert.append(index)
            graph.append(vert)
        cnt=0
        for chord in chordList:
            self.ObjectList.append(Object(1,self.strNum(chord),ch.toVect(chord,self.CONF),self))
            self.ObjectList[cnt].setIntChords(chord)
            cnt+=1
        self.MasterLines=ObjectLineS(self.ObjectList,graph,self)
        self.objList2=self.ObjectList.copy()
    def sortObject(self,event):
        dictO={}
        massLen=[]
        chor=[]
        rad=[]
        for a in range(len(self.ObjectList)):
            chor=self.ObjectList[a].geor()
            massLen.append(math.pow(math.pow(chor[0]-self.PoseChords[0],2)+math.pow(chor[1]-self.PoseChords[1],2)+math.pow(chor[2]-self.PoseChords[2],2),1/2))
            dictO[massLen[a]]=self.ObjectList[a]
        key=sorted(massLen)
        bol=False
        for i in range(len(self.ObjectList)):
            if(dictO.get(key[len(self.ObjectList)-i-1])!=self.objList2[i]):
                bol=True
        for i in range(len(self.ObjectList)):
            if(bol):
                dictO.get(key[len(self.ObjectList)-i-1]).up(self.canvas)
        self.objList2=[]
        for i in  range(len(self.ObjectList)):
            self.objList2.append(dictO.get(key[len(self.ObjectList)-i-1]))

    def sort2(self):
        dictO={}
        massLen=[]
        chor=[]
        for a in range(len(self.ObjectList)):
            chor=self.ObjectList[a].getChor()
            massLen.append(math.pow(math.pow(chor[0]-self.PoseChords[0],2)+math.pow(chor[1]-self.PoseChords[1],2)+math.pow(chor[2]-self.PoseChords[2],2),1/2))
            dictO[massLen[a]]=self.ObjectList[a]
        N=len(massLen)
        if(self.ct==len(massLen)-1):
            self.ct=0
        # if(ct==0):
        #     massLen[0]=1000
        self.ct=0
        self.sort3(massLen,N)
    def sort3(self,massLen,N):
        for i in range(N-1):
            for j in range(N-1-i):
                if massLen[j] > massLen[j+1]:
                    if(self.ObjectList[j+1].oval!="" and self.ObjectList[j].oval!=""):
                        try:
                            self.ct+=1
                            self.canvas.tag_raise(self.ObjectList[j+1].oval,self.ObjectList[j].oval)
                            massLen[j], massLen[j+1] = massLen[j+1], massLen[j]
                            self.ObjectList[j], self.ObjectList[j+1] = self.ObjectList[j+1], self.ObjectList[j]
                            self.ObjectList[j].Fix()
                            self.ObjectList[j+1].Fix()
                        except:
                            print("")
                else:
                    if(self.ObjectList[j+1].oval!="" and self.ObjectList[j].oval!=""):
                        try:
                            self.canvas.tag_raise(self.ObjectList[j].oval,self.ObjectList[j+1].oval)
                            self.ObjectList[j].Fix()
                            self.ObjectList[j+1].Fix()
                        except:
                            print("")

    def RenderObjects(self,plane,VectView,poseK,vctXY):
        inScreenDots=[]
        ovalCnt=0
        itog=True
        cnt=0
        cnt2=0
        for i in range(len(self.ObjectList)):
            try:
                self.ObjectList[i].draw( self.canvas,poseK,plane,VectView, self.size, self.VectXY)
            except:
                print(":(")
            if(not  self.dopOv):
                cnt+=1
            if( self.dvOv):
                cnt2+=1
        if(cnt==len( self.ObjectList)):
            self.massOval=False
        else:
            if(cnt2==0):
                self.massOval=False
        if( self.massOval and not  self.mouseBlock):
            self.canvas.itemconfigure( self.OvalTag, fill= self.select)
        self.canvas.tag_raise("cursor")
    def getChStr(self):
        strk=""
        for o in range(len( self.PoseChords)):
            strk+=" "+str(int( self.PoseChords[o]*100)/100)
            for i in range(6-len(str(int(math.fabs( self.PoseChords[o])*100)/100))):
                strk+=" "
        strk=strk.replace(" -","-")
        return strk
    def render(self,event):
        vctXY= self.VectXY.copy()
        VectView= mathD.rotY(vctXY[0],0,0,1)
        VectView= mathD.rotV(vctXY[1],VectView[0],VectView[1],VectView[2],-math.cos(vctXY[0]),0,math.sin(vctXY[0]))
        poseK= self.PoseChords.copy()

        ranPlane= mathD.plane(VectView, mathD.getPrDot(poseK,VectView))
        self.RenderObjects(ranPlane,VectView,poseK,vctXY)

    def w(self):
        self.PoseChords[0]+=math.cos(self.VectXY[0] + math.pi / 2)*self.step*self.kfmove
        self.PoseChords[2]-=math.sin(self.VectXY[0] + math.pi / 2)*self.step*self.kfmove
    def s(self):
        self.PoseChords[0]-=math.cos(self.VectXY[0] + math.pi / 2)*self.step*self.kfmove
        self.PoseChords[2]+=math.sin(self.VectXY[0] + math.pi / 2)*self.step*self.kfmove
    def a(self):
        self.PoseChords[0]+=math.cos(self.VectXY[0])*self.step*self.kfmove
        self.PoseChords[2]-=math.sin(self.VectXY[0])*self.step*self.kfmove
    def d(self):
        self.PoseChords[0]-=math.cos(self.VectXY[0])*self.step*self.kfmove
        self.PoseChords[2]+=math.sin(self.VectXY[0])*self.step*self.kfmove
    def space(self):
        self.PoseChords[1]+=self.step
    def shift(self):
        self.PoseChords[1]-=self.step
    def wasd(self):
        if(keyboard.is_pressed('w')): self.s();
        if(keyboard.is_pressed('s')): self.w();
        if(keyboard.is_pressed('a')): self.d();
        if(keyboard.is_pressed('d')): self.a();
        if(keyboard.is_pressed('space')): self.space();
        if(keyboard.is_pressed('shift')): self.shift();
    def razLog(self,num):
        a=num
        mass=[]
        itog=[]
        max=0
        for i in range(len(self.simpleNumbers)):
            cnt=0
            while a%self.simpleNumbers[i]==0:
                a=a//2
                cnt+=1
            if(cnt!=0):
                max=i
            mass.append(cnt)
        for i in range(max-1):
            itog.append(mass[i+1])
        return itog
    def move(self):
        global kfmove
        while True:
            if(self.focused):
                if(not self.keyBlock):
                    if not ((keyboard.is_pressed('w') and keyboard.is_pressed('a'))or(keyboard.is_pressed('w') and keyboard.is_pressed('d'))):
                        if not((keyboard.is_pressed('s') and keyboard.is_pressed('a'))or(keyboard.is_pressed('s') and keyboard.is_pressed('d'))):
                            self.kfmove=1
                        else:
                            self.kfmove=1/math.pow(2,1/2)
                    else:
                        self.kfmove=1/math.pow(2,1/2)
                    self.wasd()
                if(not self.mouseBlock):
                    self.mouse("s")
            if(self.canvas.focus_get() or self.PlayBoll):
                self.render("s")
            if(self.PlayBoll):
                self.playFrameUp()
            if(self.MasterLines!="" and self.EnabeLines):
                self.MasterLines.upDate()
            time.sleep(1/self.noFrameRate)
    def mouse(self,event):
        self.VectXY[0]+=(pyautogui.position()[0]-(self.intStats[2]+self.intStats[0]/2))*math.pi*self.mouseSens
        self.VectXY[1]-=(pyautogui.position()[1]-(self.intStats[3]+self.intStats[1]/2))*math.pi*self.mouseSens
        if(self.VectXY[1]>math.pi/2):
            self.VectXY[1]=math.pi/2
        if(self.VectXY[1]<-math.pi/2):
            self.VectXY[1]=-math.pi/2
        pyautogui.moveTo(self.intStats[2]+self.intStats[0]/2,self.intStats[3]+self.intStats[1]/2,_pause=False)
    def rendWhile(self):
        while True:
            self.render("s")
            time.sleep(1/self.framerate)
    def changeCurs(self,event):
        pyautogui.moveTo(self.intStats[2]+self.intStats[0]/2,self.intStats[3]+self.intStats[1]/2,_pause=False)
        if self.canvas.cget("cursor")=="none":
            self.canvas.config(cursor="arrow")
            self.canvas.itemconfigure(self.cursorPlus,state="hidden")
        else:
            self.canvas.config(cursor="none")
            self.canvas.itemconfigure(self.cursorPlus,state="normal")
        self.mouseBlock=not self.mouseBlock
    def enabeWASD(self,event):
        self.keyBlock= not self.keyBlock
    def objectRecreate(self,event):
        self.createObjects(self.Range,dif=self.dirCnt)

    def clearEntr(self,e):
        self.entry_text.set("n")
    def addEntr(self,chords):
        if(self.entry_text.get()=="n"):
            self.entry_text.set(self.entry_text.get()+chords)
        else:
            self.entry_text.set(self.entry_text.get()+" "+chords)
    def backSpace(self,e):
        m=self.entry_text.get()[1:]
        g=m.split(" ")
        str="n"
        if(len(g)>0):
            if(len(g)>1):
                for i in range(len(g)-1):
                    str+=g[i]
                    self.entry_text.set(str)
            else:
                self.entry_text.set("n")
    def Enabe(self,event):
        self.EntryEnabe=not self.EntryEnabe
        self.checkEntry.set(self.EntryEnabe)
    def click(self,event):
        self.canvas.focus_set()

        self.noteInstEv("")
        if(not self.mouseBlock):
            if(len(self.curentMassOval)!=0 and self.massOval):
                if(self.EntryEnabe):
                    self.addEntr(ch.chordStr(ch.r(ch.transit(self.massOvalChords,self.directions,self.simpleNumbers))))
                self.trEd=threading.Thread(target=PlayOneNote.PlayNote,args=(self.times,self.midinote,self.toLockNote(self.massOvalChords),self.tempo,self.programm,self.oct,self.rootNote,self.vel,[self.conceptOctave]+self.directions,),daemon = True)
                self.trEd.start()
        else:
            overlaping = self.canvas.find_overlapping(event.x, event.y, event.x+1, event.y+1)
            ct=-1
            for i in range(len(overlaping)):
                if("oval" in self.canvas.gettags(overlaping[i])):
                    ct=overlaping[i]
            if(ct!=-1):
                a=self.dictFromOval.get(ct).getIntChord()
                self.trEd=threading.Thread(target=PlayOneNote.PlayNote,args=(self.times,self.midinote,self.toLockNote(a),self.tempo,self.programm,self.oct,self.rootNote,self.vel,[self.conceptOctave]+self.directions,),daemon = True)
                self.trEd.start()
                self.dictFromOval.get(ct).select()
                if(self.EntryEnabe):
                    self.addEntr(ch.chordStr(ch.r(ch.transit(a,self.directions,self.simpleNumbers))))
    def addFile(self,textFile):
        name=textFile.replace("(visual).txt","")
        self.playFiles.append(name)
        f=open(textFile,"r")
        lines=f.readlines()
        if(lines[0][0]==":"):
            tNote=lines[0][1:].split(";")
            self.tempo=float(tNote[0])
            if(len(tNote)>1):
                self.midinote=int(tNote[1])
            lines=lines[1:]
        for i in range(16):
            self.AllChanDict[name+str(i)]=[]
        for s in lines:
            ms=s.split(";")
            self.AllChanDict[name+ms[4]].append(s)
        for i in range(16):
            self.AllChanDict[name+str(i)]=self.Convert(self.AllChanDict[name+str(i)])
    def Convert(self,mass):
        dictOp={}
        for i in range(len(mass)):
            str=mass[i].replace("\n","")
            str=str.split(";")
            if(str[1][0]=="_"):
                continue
            conv=ch.toFrame(self.noFrameRate,self.tempo,float(str[2]))
            lenC=ch.toFrame(self.noFrameRate,self.tempo,float(str[2])+float(str[3]))
            vect=ch.VectFcent([str[0],str[1],str[6]],self.CONF,edo=str[5])
            #  print(vect)
            intVect=ch.intChordMass([str[0],str[1],str[6]])
            if(dictOp.get(conv)==None):
                dictOp[conv]=[[vect,intVect,"on"]]
            else:
                dictOp[conv].append([vect,intVect,"on"])
            dictOp[lenC]=[[vect,intVect,"off"]]
            self.maxEv=max(self.maxEv,lenC)
        return dictOp
    def killObj(self,object):
        for o in self.ObjectList:
            if o==object:
                self.canvas.delete(o.oval)
                self.canvas.delete(o.textOval)
                # ObjectList[0]
                self.ObjectList.remove(o)
                return True
        return False
    def addObj(self,object):
        self.ObjectList.append(object)
    def Stop(self):
        self.curentFrame=0
        self.Clear()
        self.AllChanDict={}
        self.deafObj()
        self.maxEv=0
        self.playFiles=[]
        self.PlayBoll=False
    def playFrameUp(self):
        if(self.maxEv==self.curentFrame):
            self.Stop()
        for file in self.playFiles:
            for i in range(16):
                if(self.AllChanDict.get(file+str(i))!=None):
                    if(self.AllChanDict[file+str(i)].get(self.curentFrame)!=None):
                        events=self.AllChanDict[file+str(i)][self.curentFrame]
                        for ev in events:
                            if(ev[2]=="on"):
                                name=self.strNum(ev[1])
                                obj=Object(1,name,ev[0],self)
                                obj.setIntChords(ev[1])
                                self.addObj(obj)
                            if(ev[2]=="off"):
                                self.killObj(ev[0])
        self.curentFrame+=1
    def Clear(self):
        for o in self.ObjectList:
            self.canvas.delete(o.oval)
            self.canvas.delete(o.textOval)
        self.ObjectList=[]
    def mnSort(self):
        while True:
            if(self.recrateBool):
                self.upDateRecreate()
            if(not self.PlayBoll):
                self.sort2()
            time.sleep(15/self.framerate)
            self.chordEntr()
            self.setBol()
            self.EntryEnabe=self.checkEntry.get()
    def copy(self,event):
        self.root.clipboard_clear()
        self.root.clipboard_append(self.entry_text.get())
    def noteInstEv(self,event):
        self.focused=True
        PlayOneNote.init(self.intst)
    def gits(self,event):
        self.focused=False
        PlayOneNote.qit()
    def tp0(self,event):
        self.PoseChords=[0,0,0]
        self.VectXY=[0,0]
    def rgrecrate1(self,event):
        self.recrateBool=not self.recrateBool
        self.checkOt.set(self.recrateBool)
        self.poseObjVect=[self.ObjPose[0]-self.PoseChords[0],self.ObjPose[1]-self.PoseChords[1],self.ObjPose[2]-self.PoseChords[2]]
        self.intPoseK=self.PoseChords.copy()
    def addFileS(self,files):
        for f in files:
            self.addFile(f)
    def startPlay(self,files):
        self.Clear()
        self.EnabeLines=False
        self.recrateBool=False
        self.checkL.set(self.EnabeLines)
        self.checkOt.set(self.recrateBool)
        if(self.MasterLines!=""):
            self.MasterLines.clear()
        if(not self.PlayBoll):
            self.addFileS(files)
            self.PlayBoll=True
        else:
            self.Stop()
    def getContext(self):
        con=self.context_text.get()
        return con.replace("|","\n")
    def tredLog(self,file):
        toMidGa.start("file.mid")
        self.gits("")
        self.noteInstEv("")
    def playEntr(self,e):
        command=":"+str(self.tempo)+";"+str(self.midinote)+"\n"
        command+="same\n"
        command+=self.getContext()+"\n"
        command+=self.entry_text.get()+"\n"
        command+="end:note\n"
        command+="add('note')\n"
        self.gits("")
        toMidiMeth.toMidi("file",0,MIDIFile(1),line=command,fromStr=True)
        streml=threading.Thread(target=self.tredLog,args=("file.mid",),daemon=True)
        streml.start()
    def upDateRecreate(self):
        poseL=[int(self.PoseChords[0]),int(self.PoseChords[1]),int(self.PoseChords[2])]
        if([int(self.intPoseK[0]),int(self.intPoseK[1]),int(self.intPoseK[2])]!=poseL):
            self.intPoseK=self.PoseChords.copy()
            self.createObjects(self.Range,poseChords=[int(self.PoseChords[0]+self.poseObjVect[0]),int(self.PoseChords[1]+self.poseObjVect[1]),int(self.PoseChords[2]+self.poseObjVect[2])])
    def startPlayBind(self,ev):
        #print(path+"/"+file)
        self.startPlay([self.path+"/"+self.file])
    def DrewLines(self,e):
        self.EnabeLines=not self.EnabeLines
        self.checkL.set(self.EnabeLines)
        if(not self.EnabeLines):
            self.canvas.itemconfigure("line", state='hidden')
        else:
            self.canvas.itemconfigure("line", state='normal')
    def DirChange(self,ev):
        USER_INP = simpledialog.askstring(title="ПК",
                                          prompt="Измените пространство кратностей\nВведите целые числа через пробел")
        spl=USER_INP.split(" ")
        ints=[]
        for s in spl:
            if(s!=""):
                ints.append(int(s))
        self.directions=ints
    def DirCount(self,ev):
        USER_INP = simpledialog.askstring(title="куб",
                                          prompt="Колово измерений куба")
        self.dirCnt=int(USER_INP)
    def rangeDir(self,ev):
        USER_INP = simpledialog.askstring(title="куб",
                                          prompt="Точек куба")
        self.Range=int(USER_INP)
    def chordEntr(self):
        self.chord.set(str(int(self.PoseChords[0]))+" "+str(int(self.PoseChords[1]))+" "+str(int(self.PoseChords[2])))
        self.chordObj.set(str(int(self.ObjPose[0]))+" "+str(int(self.ObjPose[1]))+" "+str(int(self.ObjPose[2])))

    def Manual(self,e):
        win=tk.Toplevel()
        labelP = tk.Label(win,text="alt+f - изменение мыши\n"+
                                   "alt+f - блокировка клавиатуры\n"+
                                   "l - показать/скрыть линии\n"+
                                   "q - сгенерировать куб\n"+
                                   "u - обновить куб\n"+
                                   "t - вернуться в начало координат\n"+
                                   "e - включить/выключить запись\n"+
                                   "r - очистить записаное\n"+
                                   "b - стереть последнюю ноту\n"+
                                   "m - инструкция\n"+
                                   "F1 - запустить записаное\n"+
                                   "ctrl+f - изменить ПК\n"+
                                   "ctrl+с - скопировать записанное\n"+
                                   "h - изменить количество измерений\n"+
                                   "y - грань куба > размер\n"+
                                   "ВАЖНО!\n"+
                                   "ВСЁ ВЫШЕОПИСАННОЕ ЗАВИСИТ ОТ РАСКЛАДКИ\n И КЛАВИШИ CAPSLOCK"
                          )
        labelP.pack()
    def setBol(self):
        if(self.checkOt.get()!=self.recrateBool):
            self.rgrecrate1("")
        if(self.EnabeLines!=self.checkL.get()):
            self.DrewLines("")
    def upDateCube(self,ev):
        self.createObjects(self.Range,dir=self.dirCnt,poseChords=self.ObjPose)
    def arrayMonitoring(self):
        while True:
            h=open("playInf.txt","r")
            p=h.readline().split(":")
            h.close()
            # print(p)
            if(p[0]=="play"):
                if(not self.PlayBoll):
                    st=threading.Thread(target=self.startPlay,args=(p[1].split(" "),),daemon=True)
                    st.start()
                with open("playInf.txt", "w") as f:
                    f.write("none")
            if(p[0]=="stop"):
                self.Stop()
                with open("playInf.txt", "w") as f:
                    f.write("none")
            time.sleep(self.arrayRate*5)


class Object:
    def __init__(self,type, word,chords,base,*args,**kwargs):
        self.base=base
        self.size=kwargs.get('size',55)
        self.fill=kwargs.get('fill',"#FFFFFF")
        self.selectFill=kwargs.get('selectFill',"#FFEE95")
        self.outline=kwargs.get('outline',"#000000")
        self.type = type
        self.word = word
        self.chords = chords
        self.oval=""
        self.textOval=""
        self.chordsPlane=[0,0]
        self.CurentMass=[]
        self.intChord="?"
        self.dirChords=[0,1]
        self.inScreen=True
        self.Selected=False
        self.PlayColor=kwargs.get('PlayColor',"#a8c977")
    def setWord(self,word):
        self.word=word
    def setIntChords(self,chord):
        self.intChord=chord
    def getIntChord(self):
        if(self.intChord!="?"):
            return  self.intChord
        else:
            return self.chords
    def getChor(self):
        return self.chords
    def setType(self,type):
        self.type=type
    def Fix(self):
        try:
            self.base.canvas.tag_raise(self.textOval,self.oval)
        except:
            print("*^*")
    def up(self,canvas):
        # p=0
        canvas.tag_raise(self.oval)
        canvas.tag_raise(self.textOval)
    def down(self,canvas):
        #   p=0
        canvas.tag_lower(self.oval)
        canvas.tag_lower(self.textOval)
    def race(self,canvas,varOv):
        canvas.tag_raise(self.oval,varOv)
        canvas.tag_raise(self.textOval,varOv)
    def setDirChords(self,dir):
        self.dirChords=dir
    def getKet(self):
        return self.oval
    def visible(self):
        return self.inScreen
    def select(self):
        self.base.clearSelection()
        self.Selected=True

    def deSelect(self):
        self.Selected=False
    def __eq__(self,other):
        if not isinstance(other, (Object,list)):
            raise TypeError("not Obj")
        sc = other if isinstance(other, list) else other.chords
        return  self.chords==sc
    def draw(self,canvas,playerPose,plane,VectView,size,xyMo):
        if (plane[0]*self.chords[0]+plane[1]*self.chords[1]+plane[2]*self.chords[2]+plane[3])>0:
            self.inScreen=True
            canvas.itemconfigure(self.oval, state='normal')
            canvas.itemconfigure(self.textOval, state='normal')
            interChord=mathD.intersect(self.chords,playerPose,plane)
            pr = mathD.getPrDot(self.base.PoseChords,VectView)
            cos= mathD.xyr2(interChord,pr,xyMo)
            longOf = math.pow(math.pow((playerPose[0]-self.chords[0]),2)+math.pow((playerPose[1]-self.chords[1]),2)+math.pow((playerPose[2]-self.chords[2]),2),1/2)
            mass=[size[0]/2+(int)(cos[0]*400)*self.base.kfSize,size[1]/2-(int)(cos[1]*400)*self.base.kfSize,self.base.kfSize*self.size/longOf]
            self.CurentMass=mass
            color=self.fill
            self.base.dopOv=False
            self.base.dvOv=False
            if(not self.base.mouseBlock):
                if(math.pow(math.pow(mass[0]-size[0]/2,2)+math.pow(mass[1]-size[1]/2,2),1/2)<mass[2]):
                    self.base.dopOv=True
                    if(not self.base.massOval):
                        self.base.curentMassOval=mass
                        if(self.intChord!="?"):
                            self.base.massOvalChords=self.intChord
                        else:
                            self.base.massOvalChords=self.chords
                        self.base.massOval=True
                        self.base.OvalTag=self.oval
                        self.base.select=self.selectFill
                    else:
                        try:
                            if(math.pow(math.pow(self.base.PoseChords[0]-self.chords[0],2)+math.pow(self.base.PoseChords[1]-self.chords[1],2)+math.pow(self.base.PoseChords[2]-self.chords[2],2),1/2)<
                                    math.pow(math.pow(self.base.PoseChords[0]-self.base.massOvalChords[0],2)+math.pow(self.base.PoseChords[1]-self.base.massOvalChords[1],2)+math.pow(self.base.PoseChords[2]-self.base.massOvalChords[2],2),1/2)):
                                self.base.curentMassOval=mass
                                if(self.intChord!="?"):
                                    self.base.massOvalChords=self.intChord
                                else:
                                    self.base.massOvalChords=self.chords
                                self.base.OvalTag=self.oval
                                self.base.select=self.selectFill
                        except:
                            print("")
                    if(self.oval==self.base.OvalTag):
                        self.base.dvOv=True
            if(self.oval==""):
                self.oval=canvas.create_oval(mass[0]-mass[2],mass[1]-mass[2],mass[0]+mass[2],mass[1]+mass[2],fill=color,tags=["oval"])
                self.base.ovals.append(self.oval)
                self.textOval=canvas.create_text(mass[0], mass[1], anchor=NW, text=self.word, fill=self.outline,tags=["text"])
                self.base.words.append(self.textOval)
                self.base.dictFromOval[self.oval]=self
            else:
                coordx = mass[0]-mass[2],mass[1]-mass[2],mass[0]+mass[2],mass[1]+mass[2]
                chord2 = mass[0],mass[1]
                self.dirChords=[mass[0],mass[1]]
                canvas.coords(self.oval, coordx)
                canvas.coords(self.textOval, chord2)
            if(not self.base.PlayBoll):
                if(not self.base.mouseBlock):
                    if(self.base.massOval):
                        if(self.oval!=self.base.OvalTag):
                            canvas.itemconfigure(self.oval, fill=color,outline=self.outline)
                    else:
                        canvas.itemconfigure(self.oval, fill=color,outline=self.outline)
                else:
                    if(self.Selected):
                        canvas.itemconfigure(self.oval, fill=self.selectFill,outline=self.outline)
                    else:
                        canvas.itemconfigure(self.oval, fill=self.fill,outline=self.outline)
            else:
                canvas.itemconfigure(self.oval, fill=self.PlayColor,outline=self.PlayColor)
                canvas.tag_raise(self.textOval)
            self.chordsPlane=mass
            self.base.inScreenDots.append(mass)
            self.base.DotsChord.append(self.chords)
            self.base.ovalCnt+=1
        else:
            self.inScreen=False
            canvas.itemconfigure(self.oval, state='hidden')
            canvas.itemconfigure(self.textOval, state='hidden')
class Line:
    def __init__(self,Object1, Object2,base,**kwargs):
        self.base=base
        self.obj1=Object1
        self.obj2=Object2
        self.color=self.getDirChange(self.obj1.getIntChord(),self.obj2.getIntChord())
        self.line=self.base.canvas.create_line(self.obj1.dirChords[0],self.obj1.dirChords[1],self.obj2.dirChords[0],self.obj2.dirChords[1],tags=["line"],fill=self.color,width=2)
        #canvas.itemconfigure(self.line,fill)
    def getDirChange(self,chord1,chord2):
        for i in range(len(chord2)):
            if(chord1[i]!=chord2[i]):
                return self.base.colorConfig[i]
        return "#000000"
    def uppdate(self):
        chords=self.obj1.dirChords[0],self.obj1.dirChords[1],self.obj2.dirChords[0],self.obj2.dirChords[1]
        if(not self.obj1.inScreen or not self.obj2.inScreen):
            self.base.canvas.itemconfigure(self.line,state="hidden")
        else:
            self.base.canvas.itemconfigure(self.line,state="normal")
        self.base.canvas.coords(self.line,chords)
    def __eq__(self,other):
        if not isinstance(other, (Line,list)):
            raise TypeError("not Obj")
        if isinstance(other, list):
            if(len(other)!=2):
                return False
            if(other[0]==self.obj1 and other[1]==self.obj2):
                return True
            if(other[1]==self.obj1 and other[0]==self.obj2):
                return True
            return False
        else:
            if(other.obj1==self.obj1 and other.obj2==self.obj2):
                return True
            if(other.obj2==self.obj1 and other.obj1==self.obj2):
                return True
            return False
class ObjectLineS:
    def inLines(self,line):
        for l in self.lines:
            if l==line:
                return True
        return False
    def __init__(self,ObjectList, Graph,base,**kwargs):
        self.lines=[]
        self.base=base
        for a in range(len(ObjectList)):
            for b in range(len(Graph[a])):
                mass=[ObjectList[a],ObjectList[Graph[a][b]]]
                if(mass[0]!=mass[1]):
                    if not self.inLines(mass):
                        self.lines.append(Line(mass[0],mass[1],base))
    def clear(self):
        for l in self.lines:
            self.base.canvas.delete("line")
    def upDate(self):
        for l in self.lines:
            l.uppdate()
#root =tk.Tk()
#Graph(root,winStats="450x450+600+300")

#canvasS(root,path="music/visual",file="chord(visual).txt",winStats="450x450+600+300")

#root.mainloop()