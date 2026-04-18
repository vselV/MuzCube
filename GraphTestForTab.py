import math
import pyautogui
import tkinter as tk
from tkinter import ttk, simpledialog
from tkinter import *
import src.MuzCube.FirstVersion.toMidiMeth, src.MuzCube.FirstVersion.toMidGa
from midiutil import MIDIFile
import threading
import re
import keyboard
import time
import src.MuzCube.FirstVersion.PlayOneNote
import ch






def canvasS(root,*args, **kwargs):
    pyautogui.FAILSAFE=False

    allFrame = ttk.Frame( relief=SOLID, padding=[8, 10])
    FrameStats=ttk.Frame(allFrame)

    array=kwargs.get('array', [])
    arrayRate=0.02
   # array.append("arr")
    print(array)
    EnabeLines=False

    defDir=[3,5,7,11,13,17,19]
    dirCnt=3
    colorConfig=["#994242","#699942","#42528a","#654299","#429998","#997642"]
    conceptOctave=kwargs.get('conceptOctave', 2)
    #fly
    path=kwargs.get('path', "")
    file=kwargs.get('file', "")
    Range=2


    directions=kwargs.get('directions', defDir)
    axsis=kwargs.get('axsis', False)
    winStats=kwargs.get('winStats',"800x800+300+300")
    mouseBlock=kwargs.get('mouseBlock',True)
    keyBlock=kwargs.get('mouseBlock',True)
    kfSize=kwargs.get('kfSize',2)
    cursorColor=kwargs.get('cursorColor',"#000000")
    cursorText=kwargs.get('cursorText',"+")
    intst=kwargs.get('inst',0)
    configVect=kwargs.get('configVect',"configVectors")
    CONF=ch.readConfig(configVect)
    rePointRate=kwargs.get('rePointRate',0.1 )
    dictFromOval={}
    dirCount=3
    inScreenDots=[]
    DotsChord=[]

    mousepose = pyautogui.position()

    VectXY =[0,0]
    VectView = [0,0,1]
    PoseChords = [0.5,0.5,-5]
    intPoseK=[0,0,0]
    ##
    ObjPose=[0,0,0]
    poseObjVect=[0,0,0]
    recrateBool=False
    ##
    lastpose=[0,0,0]

    framerate=50
    filesPlay=["file."]


    splitStats = re.split("\\+|x",winStats)
    intStats=[int(splitStats[0]),int(splitStats[1]),int(splitStats[2]),int(splitStats[3])]
    size=[intStats[0],intStats[1]]

    MasterLines=""

    ovalCnt=0
    ovals=[]
    words=[]

    curentMassOval=[]
    massOvalChords=[]
    OvalTag=""
    select=''
    massOval=False
    dopOv=False
    dvOv=False

    octave=0
    conLen="#"
    curLen="#"
    conVel=80

    mouseSens=0.002

    noFrameRate=40

    step=0.10
    wk=False
    ak=False
    sk=False
    dk=False
    #play
    tempo=kwargs.get('tempo',120)
    times=kwargs.get('time',1)
    programm=kwargs.get('programm',1)
    midinote=kwargs.get('midinote',60)
    oct=kwargs.get('oct',0)
    vel=kwargs.get('vel',80)
    rootNote=kwargs.get('rootNote',"0")
    simpleNumbers=kwargs.get('simpleNumbers',[2,3,5,7,11,13,17,19,23])
    dictObj={}
    objList2=[]

    focused=False

    canvas = Canvas(allFrame,bg="white", width=int(splitStats[0]), height=int(splitStats[1]))

    cursorPlus=canvas.create_text(intStats[0]/2-5,intStats[1]/2-5,anchor=NW,text=cursorText,fill=cursorColor,state="hidden",tags=["cursor"])

    entry_text = tk.StringVar()
    entry = tk.Entry(allFrame, textvariable=entry_text ,bg="grey87",fg="NavyBlue", width=int(size[0]/10))
    context_text = tk.StringVar()
    context_entry = tk.Entry(allFrame, textvariable=context_text ,bg="grey87",fg="NavyBlue", width=int(size[0]/12))
    entry_text.set("n")

    checkL = tk.BooleanVar(value=False)
    check_lines = ttk.Checkbutton(FrameStats,text="Lines", variable=checkL)

    checkOt=tk.BooleanVar(value=False)
    checkOO= ttk.Checkbutton(FrameStats,text="Fixed Cube", variable=checkOt)

    chord=tk.StringVar()
    entry_cords=tk.Entry(FrameStats, textvariable=chord ,bg="grey87",fg="NavyBlue", width=20,state="readonly")
    chordObj=tk.StringVar()
    entry_Objcords=tk.Entry(FrameStats, textvariable=chordObj ,bg="grey87",fg="NavyBlue", width=20,state="readonly")

    EntryEnabe=False

    #chekboxes
    checkEntry = tk.BooleanVar(value=EntryEnabe)
    EntryBox = ttk.Checkbutton(allFrame,text="Rec", variable=checkEntry)

    entry_cords.pack()
    entry_Objcords.pack()
    check_lines.pack()
    checkOO.pack()

    PlayBoll=False
    curentFrame=0
    AllChanDict={}
    playFiles=[]
    maxEv=0

    def rotM(rx,ry,rz,x,y,z):
        chordIn = [0,0,0]
        ak=math.sin(rx)
        bk=math.sin(ry)
        ck=math.sin(rz)
        ac=math.cos(rx)
        bc=math.cos(ry)
        cc=math.cos(rz)
        chordIn[0]=bc*cc*x-ck*bc*y+bc*z
        chordIn[1]=(ak*bk*cc+ck*ac)*x+(-ak*bk*ck+ac*cc)*y-ak*bc*z
        chordIn[2]=(ak*ck-bk*ac*cc)*x+(ak*cc+bk*ck*ac)*y+ac*bc*z
        return chordIn
    def rotY(ry,x,y,z):
        cord =[0,0,0]
        cord[0] = math.cos(ry)*x+math.sin(ry)*z
        cord[1] =y
        cord[2] =-math.sin(ry)*x+math.cos(ry)*z
        return cord
    def rotV(r, x, y, z, u1, u2, u3):
        cord =[0,0,0]
        c = math.cos(r)
        s = math.sin(r)
        cord[0] =(c+(1-c)*u1*u1)*x+((1-c)*u2*u1-s*u3)*y+((1-c)*u3*u1+s*u2)*z
        cord[1] =((1-c)*u1*u2+s*u3)*x+(c+(1-c)*u2*u2)*y+((1-c)*u3*u2-s*u1)*z
        cord[2] =((1-c)*u1*u3-s*u2)*x+((1-c)*u2*u3+s*u1)*y+(c+(1-c)*u3*u3)*z
        return cord
    def getPrDot(pose,vect):
        ans = [pose[0]+vect[0],pose[1]+vect[1],pose[2]+vect[2]]
        return ans
    def plane(abc,prDot):
        ansPlane = [abc[0],abc[1],abc[2],-(abc[0]*prDot[0]+abc[1]*prDot[1]+abc[2]*prDot[2])]
        return ansPlane
    def intersect(pxyz,qxyz,plane):
        tDenom=plane[0]*(qxyz[0]-pxyz[0])+plane[1]*(qxyz[1]-pxyz[1])+plane[2]*(qxyz[2]-pxyz[2])+0.000001
        t = -(plane[0]*pxyz[0]+plane[1]*pxyz[1]+plane[2]*pxyz[2]+plane[3])/tDenom
        ans = [pxyz[0]+t*(qxyz[0]-pxyz[0]),pxyz[1]+t*(qxyz[1]-pxyz[1]),pxyz[2]+t*(qxyz[2]-pxyz[2])]
        return ans
    def xyr2(inter,pr,XYmo):
        nvect=[inter[0]-pr[0],inter[1]-pr[1],inter[2]-pr[2]]
        VectIV2 =rotV(-XYmo[1],nvect[0],nvect[1],nvect[2],-math.cos(XYmo[0]),0,math.sin(XYmo[0]))
        VectIV2=rotY(-XYmo[0],VectIV2[0],VectIV2[1],VectIV2[2])
        ans =[VectIV2[0],VectIV2[1]]
        return ans
    class Object:
        def __init__(self,type, word,chords,*args,**kwargs):
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
                canvas.tag_raise(self.textOval,self.oval)
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
            nonlocal clearSelection
            clearSelection()
            self.Selected=True

        def deSelect(self):
            self.Selected=False
        def __eq__(self,other):
            if not isinstance(other, (Object,list)):
                raise TypeError("not Obj")
            sc = other if isinstance(other, list) else other.chords
            return  self.chords==sc
        def draw(self,canvas,playerPose,plane,VectView,size,xyMo):
            nonlocal inScreenDots
            nonlocal curentMassOval
            nonlocal massOvalChords
            nonlocal ovalCnt
            nonlocal dictObj,massOval,dopOv,select,OvalTag,dvOv,dictFromOval
            if (plane[0]*self.chords[0]+plane[1]*self.chords[1]+plane[2]*self.chords[2]+plane[3])>0:
                self.inScreen=True
                canvas.itemconfigure(self.oval, state='normal')
                canvas.itemconfigure(self.textOval, state='normal')
                interChord=intersect(self.chords,playerPose,plane)
                pr = getPrDot(PoseChords,VectView)
                cos=xyr2(interChord,pr,xyMo)
                longOf = math.pow(math.pow((playerPose[0]-self.chords[0]),2)+math.pow((playerPose[1]-self.chords[1]),2)+math.pow((playerPose[2]-self.chords[2]),2),1/2)
                mass=[size[0]/2+(int)(cos[0]*400)*kfSize,size[1]/2-(int)(cos[1]*400)*kfSize,kfSize*self.size/longOf]
                self.CurentMass=mass
                color=self.fill
                dopOv=False
                dvOv=False
                if(not mouseBlock):
                    if(math.pow(math.pow(mass[0]-size[0]/2,2)+math.pow(mass[1]-size[1]/2,2),1/2)<mass[2]):
                        dopOv=True
                        if(not massOval):
                            curentMassOval=mass
                            if(self.intChord!="?"):
                                massOvalChords=self.intChord
                            else:
                                massOvalChords=self.chords
                            massOval=True
                            OvalTag=self.oval
                            select=self.selectFill
                        else:
                         #   print(self.chords)
                             try:
                                if(math.pow(math.pow(PoseChords[0]-self.chords[0],2)+math.pow(PoseChords[1]-self.chords[1],2)+math.pow(PoseChords[2]-self.chords[2],2),1/2)<
                                        math.pow(math.pow(PoseChords[0]-massOvalChords[0],2)+math.pow(PoseChords[1]-massOvalChords[1],2)+math.pow(PoseChords[2]-massOvalChords[2],2),1/2)):
                                    curentMassOval=mass
                                    if(self.intChord!="?"):
                                        massOvalChords=self.intChord
                                    else:
                                        massOvalChords=self.chords
                                    OvalTag=self.oval
                                    select=self.selectFill
                             except:
                                print("*_*")

                        if(self.oval==OvalTag):
                            dvOv=True
                if(self.oval==""):
                    self.oval=canvas.create_oval(mass[0]-mass[2],mass[1]-mass[2],mass[0]+mass[2],mass[1]+mass[2],fill=color,tags=["oval"])
                    ovals.append(self.oval)
                    self.textOval=canvas.create_text(mass[0], mass[1], anchor=NW, text=self.word, fill=self.outline,tags=["text"])
                    words.append(self.textOval)
                    dictFromOval[self.oval]=self
                else:
                    coordx = mass[0]-mass[2],mass[1]-mass[2],mass[0]+mass[2],mass[1]+mass[2]
                    chord2 = mass[0],mass[1]
                    self.dirChords=[mass[0],mass[1]]
                    canvas.coords(self.oval, coordx)
                    canvas.coords(self.textOval, chord2)
                if(not PlayBoll):
                    if(not mouseBlock):
                        if(massOval):
                            if(self.oval!=OvalTag):
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
                inScreenDots.append(mass)
                DotsChord.append(self.chords)
                ovalCnt+=1
            else:
                self.inScreen=False
                canvas.itemconfigure(self.oval, state='hidden')
                canvas.itemconfigure(self.textOval, state='hidden')
    class Line:
        def getDirChange(self,chord1,chord2):
            nonlocal colorConfig
            for i in range(len(chord2)):
                if(chord1[i]!=chord2[i]):
                    return colorConfig[i]
            return "#000000"
        def __init__(self,Object1, Object2,**kwargs):
            self.obj1=Object1
            self.obj2=Object2
            self.color=self.getDirChange(self.obj1.getIntChord(),self.obj2.getIntChord())
            self.line=canvas.create_line(self.obj1.dirChords[0],self.obj1.dirChords[1],self.obj2.dirChords[0],self.obj2.dirChords[1],tags=["line"],fill=self.color,width=2)
            #canvas.itemconfigure(self.line,fill)
        def uppdate(self):
            chords=self.obj1.dirChords[0],self.obj1.dirChords[1],self.obj2.dirChords[0],self.obj2.dirChords[1]
            if(not self.obj1.inScreen or not self.obj2.inScreen):
                canvas.itemconfigure(self.line,state="hidden")
            else:
                canvas.itemconfigure(self.line,state="normal")
            canvas.coords(self.line,chords)
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
        def __init__(self,ObjectList, Graph,**kwargs):
            self.lines=[]
            for a in range(len(ObjectList)):
                for b in range(len(Graph[a])):
                    mass=[ObjectList[a],ObjectList[Graph[a][b]]]
                    if(mass[0]!=mass[1]):
                        if not self.inLines(mass):
                            self.lines.append(Line(mass[0],mass[1]))
        def clear(self):
            for l in self.lines:
                canvas.delete("line")
        def upDate(self):
            for l in self.lines:
                l.uppdate()
    ObjectList = []
    objList2=ObjectList.copy()
    def deafObj():
        nonlocal ObjectList
        createObjects(Range,dir=dirCnt,poseChords=ObjPose)
      #  ObjectList=[Object(1,"note",[0,0,2])]
    def clearSelection():
        for o in ObjectList:
            o.deSelect()
    def toLockNote(chords):
        ans=""
        for j in chords:
            ans+=str(j)+"."
        ans=ans[0:len(ans)-1]
        return ans
    def getNum(nump):
        # print(nump)
        m=nump.split(".")
        intA=[1,1]
        for i in range(len(m)):
            try:
                if(int(m[i])>0):
                    intA[0]=intA[0]*math.pow(directions[i],int(m[i]))
            except:
                intA[0]=404
            try:
                if(int(m[i])<0):
                    intA[1]=intA[1]*math.pow(directions[i],-int(m[i]))
            except:
                intA[1]=404
        return intA
    def getNumSt(nump):
        m=nump.split(".")
        intA=1
        for i in range(len(m)):
            try:
                intA=intA*math.pow(directions[i],int(m[i]))
            except:
                intA=404
        return intA
    def tPose(num,num2):
        nnum=num
        j=num2
        c1=0;c2=0
        while(j>conceptOctave):
            j=j/conceptOctave
            nnum[1]=nnum[1]*conceptOctave
        while(j<1):
            c2+=1
            j=j*conceptOctave
            nnum[0]=nnum[0]*conceptOctave
        return [int(nnum[0]),int(nnum[1])]
    def strNum(chords):
        if(chords=="?"):
            return chords
        stA=toLockNote(chords)
        mNum=tPose(getNum(stA),getNumSt(stA))
        return str(mNum[0])+"/"+str(mNum[1])
    def createObjects(ranGe,**kwargs):
        nonlocal ObjectList,ovals,words,objList2,ObjPose,MasterLines,intPoseK,poseObjVect
        dirCt=kwargs.get("dir",3)
        poseChords=kwargs.get("poseChords",PoseChords)
        if(MasterLines!=""):
            MasterLines.clear()
      #  intPoseK=[int(PoseChords[0]),int(poseChords[1]),int(poseChords[2])]
        locDir=[]
        for i in range(dirCt):
            locDir.append(directions[i])
        for ov in ovals:
            canvas.delete(ov)
        for wd in words:
            canvas.delete(wd)
        dt=[]
        if(dirCt<len(directions)):
            for i in range(dirCt):
                dt.append(directions[i])
        else:
            dt=directions
        ovals=[]
        words=[]
        ObjectList=[]
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

        ItDir=min(dirCt,len(directions))
        if(ItDir>3):
            for i in range(ItDir-3):
                intPose.append(1)
        ObjPose=poseChords.copy()
        #(recrateBool):
            #poseObjVect=[PoseChords[0]-poseChords[0],PoseChords[1]-poseChords[1],PoseChords[2]-poseChords[2]]
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
            ObjectList.append(Object(1,strNum(chord),ch.toVect(chord,CONF)))
            ObjectList[cnt].setIntChords(chord)
            cnt+=1
        MasterLines=ObjectLineS(ObjectList,graph)
        objList2=ObjectList.copy()
    def sortObject(event):
        nonlocal  objList2
        dictO={}
        massLen=[]
        chor=[]
        rad=[]
        for a in range(len(ObjectList)):
            chor=ObjectList[a].getChor()
            massLen.append(math.pow(math.pow(chor[0]-PoseChords[0],2)+math.pow(chor[1]-PoseChords[1],2)+math.pow(chor[2]-PoseChords[2],2),1/2))
            dictO[massLen[a]]=ObjectList[a]
        key=sorted(massLen)
        bol=False
        for i in range(len(ObjectList)):
            if(dictO.get(key[len(ObjectList)-i-1])!=objList2[i]):
                bol=True
        for i in range(len(ObjectList)):
            if(bol):
                dictO.get(key[len(ObjectList)-i-1]).up(canvas)
        objList2=[]
        for i in  range(len(ObjectList)):
            objList2.append(dictO.get(key[len(ObjectList)-i-1]))
    ct=0
    def sort2():
        nonlocal ct
        dictO={}
        massLen=[]
        chor=[]
        for a in range(len(ObjectList)):
            chor=ObjectList[a].getChor()
            massLen.append(math.pow(math.pow(chor[0]-PoseChords[0],2)+math.pow(chor[1]-PoseChords[1],2)+math.pow(chor[2]-PoseChords[2],2),1/2))
            dictO[massLen[a]]=ObjectList[a]
        N=len(massLen)
        if(ct==len(massLen)-1):
            ct=0
       # if(ct==0):
       #     massLen[0]=1000
        ct=0
        sort3(massLen,N)

    def sort3(massLen,N):
        nonlocal ObjectList,ct
        for i in range(N-1):
            for j in range(N-1-i):
                if massLen[j] > massLen[j+1]:
                    if(ObjectList[j+1].oval!="" and ObjectList[j].oval!=""):
                        try:
                            ct+=1
                            canvas.tag_raise(ObjectList[j+1].oval,ObjectList[j].oval)
                           # canvas.tag_lower(ObjectList[j].oval,ObjectList[j+1].oval)
                            massLen[j], massLen[j+1] = massLen[j+1], massLen[j]
                            ObjectList[j], ObjectList[j+1] = ObjectList[j+1], ObjectList[j]
                            ObjectList[j].Fix()
                            ObjectList[j+1].Fix()
                        except:
                            print("*_*")
                     #   ObjectList[j].Fix()
                       # ObjectList[j+1].Fix()
                else:
                    if(ObjectList[j+1].oval!="" and ObjectList[j].oval!=""):
                        try:
                            canvas.tag_raise(ObjectList[j].oval,ObjectList[j+1].oval)
                            ObjectList[j].Fix()
                            ObjectList[j+1].Fix()
                        except:
                            print("*_*")

                       # dictO[massLen[j+1]].Fix()
                       # dictO[massLen[j]].Fix()

     #   print(massLen)
    def RenderObjects(plane,VectView,poseK,vctXY):
        nonlocal curentMassOval,massOvalChords, ovalCnt,massOval
        inScreenDots=[]
        ovalCnt=0
        itog=True
        cnt=0
        cnt2=0
        for i in range(len(ObjectList)):
            try:
               ObjectList[i].draw(canvas,poseK,plane,VectView,size,VectXY)
            except:
                print(":(")
            if(not dopOv):
                cnt+=1
            if(dvOv):
                cnt2+=1
        if(cnt==len(ObjectList)):
            massOval=False
        else:
            if(cnt2==0):
                massOval=False
        if(massOval and not mouseBlock):
            canvas.itemconfigure(OvalTag, fill=select)
        canvas.tag_raise("cursor")
    def getChStr():
        strk=""
        for o in range(len(PoseChords)):
            strk+=" "+str(int(PoseChords[o]*100)/100)
            for i in range(6-len(str(int(math.fabs(PoseChords[o])*100)/100))):
                strk+=" "
        strk=strk.replace(" -","-")
        return strk
    def render(event):
        vctXY=VectXY.copy()
        VectView=rotY(vctXY[0],0,0,1);
        VectView=rotV(vctXY[1],VectView[0],VectView[1],VectView[2],-math.cos(vctXY[0]),0,math.sin(vctXY[0]));
        poseK=PoseChords.copy()

        ranPlane=plane(VectView,getPrDot(poseK,VectView))
        RenderObjects(ranPlane,VectView,poseK,vctXY)
    kfmove=1
    def w():
        PoseChords[0]+=math.cos(VectXY[0] + math.pi / 2)*step*kfmove
        PoseChords[2]-=math.sin(VectXY[0] + math.pi / 2)*step*kfmove
    def s():
        PoseChords[0]-=math.cos(VectXY[0] + math.pi / 2)*step*kfmove
        PoseChords[2]+=math.sin(VectXY[0] + math.pi / 2)*step*kfmove
    def a():
        PoseChords[0]+=math.cos(VectXY[0])*step*kfmove
        PoseChords[2]-=math.sin(VectXY[0])*step*kfmove
    def d():
        PoseChords[0]-=math.cos(VectXY[0])*step*kfmove
        PoseChords[2]+=math.sin(VectXY[0])*step*kfmove
    def space():
        PoseChords[1]+=step
    def shift():
        PoseChords[1]-=step
    def wasd():
        #print(wk)
        if(keyboard.is_pressed('w')): s();
        if(keyboard.is_pressed('s')): w();
        if(keyboard.is_pressed('a')): d();
        if(keyboard.is_pressed('d')): a();
        if(keyboard.is_pressed('space')): space();
        if(keyboard.is_pressed('shift')): shift();
    def razLog(num):
        a=num
        mass=[]
        itog=[]
        max=0
        for i in range(len(simpleNumbers)):
            cnt=0
            while a%simpleNumbers[i]==0:
                a=a//2
                cnt+=1
            if(cnt!=0):
                max=i
            mass.append(cnt)
        for i in range(max-1):
            itog.append(mass[i+1])
        return itog
    def move():
        global kfmove
        while True:
            if(focused):
                if(not keyBlock):
                    if not ((keyboard.is_pressed('w') and keyboard.is_pressed('a'))or(keyboard.is_pressed('w') and keyboard.is_pressed('d'))):
                       if not((keyboard.is_pressed('s') and keyboard.is_pressed('a'))or(keyboard.is_pressed('s') and keyboard.is_pressed('d'))):
                           kfmove=1
                       else:
                            kfmove=1/math.pow(2,1/2)
                    else:
                        kfmove=1/math.pow(2,1/2)
                    wasd()
                if(not mouseBlock):
                    mouse("s")
            if(canvas.focus_get() or PlayBoll):
                render("s")
            if(PlayBoll):
                playFrameUp()
            if(MasterLines!="" and EnabeLines):
                MasterLines.upDate()
           # sortObject("")
            time.sleep(1/noFrameRate)
    def mouse(event):
        VectXY[0]+=(pyautogui.position()[0]-(intStats[2]+intStats[0]/2))*math.pi*mouseSens;
        VectXY[1]-=(pyautogui.position()[1]-(intStats[3]+intStats[1]/2))*math.pi*mouseSens;
        if(VectXY[1]>math.pi/2):
            VectXY[1]=math.pi/2
        if(VectXY[1]<-math.pi/2):
            VectXY[1]=-math.pi/2
        pyautogui.moveTo(intStats[2]+intStats[0]/2,intStats[3]+intStats[1]/2,_pause=False)
    def rendWhile():
        while True:
            render("s")
            time.sleep(1/framerate)
    def changeCurs(event):
        nonlocal mouseBlock
        pyautogui.moveTo(intStats[2]+intStats[0]/2,intStats[3]+intStats[1]/2,_pause=False)
        print("t")
        if canvas.cget("cursor")=="none":
            canvas.config(cursor="arrow")
            canvas.itemconfigure(cursorPlus,state="hidden")
        else:
            canvas.config(cursor="none")
            canvas.itemconfigure(cursorPlus,state="normal")
        mouseBlock=not mouseBlock
    def enabeWASD(event):
        nonlocal keyBlock
        keyBlock= not keyBlock
    def objectRecreate(event):
        createObjects(Range,dif=dirCnt)
    trEd=""
    def clearEntr(e):
        nonlocal entry_text
        entry_text.set("n")
    def addEntr(chords):
        nonlocal entry_text
        print(entry_text.get)
        if(entry_text.get()=="n"):
            entry_text.set(entry_text.get()+chords)
        else:
            entry_text.set(entry_text.get()+" "+chords)
        #print(entry_text.get)
    def backSpace(e):
        m=entry_text.get()[1:]
        g=m.split(" ")
        str="n"
        if(len(g)>0):
            if(len(g)>1):
                for i in range(len(g)-1):
                    str+=g[i]
                    entry_text.set(str)
            else:
                entry_text.set("n")
    def Enabe(event):
        nonlocal EntryEnabe,checkEntry
        EntryEnabe=not EntryEnabe
        checkEntry.set(EntryEnabe)
    def click(event):
        canvas.focus_set()
        nonlocal trEd
        noteInstEv("")
        print("click")
        if(not mouseBlock):
            if(len(curentMassOval)!=0 and massOval):
                if(EntryEnabe):
                    addEntr(ch.chordStr(ch.r(ch.transit(massOvalChords,directions,simpleNumbers))))
                trEd=threading.Thread(target=PlayOneNote.PlayNote,args=(times,midinote,toLockNote(massOvalChords),tempo,programm,oct,rootNote,vel,[conceptOctave]+directions,),daemon = True)
                trEd.start()
        else:
            overlaping = canvas.find_overlapping(event.x, event.y, event.x+1, event.y+1)
            ct=-1
            for i in range(len(overlaping)):
                if("oval" in canvas.gettags(overlaping[i])):
                    ct=overlaping[i]
            if(ct!=-1):
                a=dictFromOval.get(ct).getIntChord()
                trEd=threading.Thread(target=PlayOneNote.PlayNote,args=(times,midinote,toLockNote(a),tempo,programm,oct,rootNote,vel,[conceptOctave]+directions,),daemon = True)
                trEd.start()
                dictFromOval.get(ct).select()
                if(EntryEnabe):
                    addEntr(ch.chordStr(ch.r(ch.transit(a,directions,simpleNumbers))))
    def addFile(textFile):
        nonlocal playFiles,AllChanDict,tempo,midinote
        name=textFile.replace("(visual).txt","")
        playFiles.append(name)
        print(textFile)
        f=open(textFile,"r")
        lines=f.readlines()
        if(lines[0][0]==":"):
            tNote=lines[0][1:].split(";")
            tempo=float(tNote[0])
            if(len(tNote)>1):
                midinote=int(tNote[1])
            lines=lines[1:]
        for i in range(16):
            AllChanDict[name+str(i)]=[]
        for s in lines:
            ms=s.split(";")
            AllChanDict[name+ms[4]].append(s)
        for i in range(16):
            AllChanDict[name+str(i)]=Convert(AllChanDict[name+str(i)])
    def Convert(mass):
        nonlocal maxEv
        dictOp={}
        for i in range(len(mass)):
            str=mass[i].replace("\n","")
            str=str.split(";")
            if(str[1][0]=="_"):
                continue
            conv=ch.toFrame(noFrameRate,tempo,float(str[2]))
            lenC=ch.toFrame(noFrameRate,tempo,float(str[2])+float(str[3]))
            vect=ch.VectFcent([str[0],str[1],str[6]],CONF,edo=str[5])
          #  print(vect)
            intVect=ch.intChordMass([str[0],str[1],str[6]])
            if(dictOp.get(conv)==None):
                dictOp[conv]=[[vect,intVect,"on"]]
            else:
                dictOp[conv].append([vect,intVect,"on"])
            dictOp[lenC]=[[vect,intVect,"off"]]
            maxEv=max(maxEv,lenC)
        return dictOp
    def killObj(object):
        for o in ObjectList:
            if o==object:
                canvas.delete(o.oval)
                canvas.delete(o.textOval)
               # ObjectList[0]
                ObjectList.remove(o)
                return True
        return False
    def addObj(object):
        ObjectList.append(object)
    def Stop():
        nonlocal AllChanDict,PlayBoll,maxEv,playFiles,curentFrame
        curentFrame=0
        Clear()
        AllChanDict={}
        deafObj()
        maxEv=0
        playFiles=[]
        PlayBoll=False
    def playFrameUp():
        nonlocal curentFrame
        if(maxEv==curentFrame):
            Stop()
        for file in playFiles:
            for i in range(16):
                if(AllChanDict.get(file+str(i))!=None):
                    if(AllChanDict[file+str(i)].get(curentFrame)!=None):
                        events=AllChanDict[file+str(i)][curentFrame]
                      #  print(events)
                        for ev in events:
                         #   print(ev)
                            if(ev[2]=="on"):
                                name=strNum(ev[1])
                                obj=Object(1,name,ev[0])
                                obj.setIntChords(ev[1])
                                addObj(obj)
                            if(ev[2]=="off"):
                                killObj(ev[0])
                              #  print(killObj(ev[0]))
       # sort2()
        curentFrame+=1
    def Clear():
        nonlocal ObjectList
        for o in ObjectList:
            canvas.delete(o.oval)
            canvas.delete(o.textOval)
        ObjectList=[]
    def mnSort():
        nonlocal EntryEnabe
        while True:
            if(recrateBool):
                upDateRecreate()
            if(not PlayBoll):
                sort2()
            time.sleep(15/framerate)
            chordEntr()
            setBol()
            EntryEnabe=checkEntry.get()
    def copy(event):
        root.clipboard_clear()
        root.clipboard_append(entry_text.get())
    def noteInstEv(event):
        nonlocal focused
        focused=True
        PlayOneNote.init(intst)
    def gits(event):
        nonlocal focused
        focused=False
        PlayOneNote.qit()
    def tp0(event):
        nonlocal PoseChords, VectXY
        PoseChords=[0,0,0]
        VectXY=[0,0]
    def rgrecrate1(event):
        nonlocal recrateBool,poseObjVect,intPoseK
        recrateBool=not recrateBool
        checkOt.set(recrateBool)
        print(ObjPose)
        print(PoseChords)
        poseObjVect=[ObjPose[0]-PoseChords[0],ObjPose[1]-PoseChords[1],ObjPose[2]-PoseChords[2]]
        intPoseK=PoseChords.copy()
    def addFileS(files):
        for f in files:
            addFile(f)
    def startPlay(files):
        nonlocal PlayBoll,AllChanDict,EnabeLines,recrateBool
        Clear()
        EnabeLines=False
        recrateBool=False
        checkL.set(EnabeLines)
        checkOt.set(recrateBool)
        if(MasterLines!=""):
            MasterLines.clear()
        if(not PlayBoll):
            addFileS(files)
            print("POPOPOPOPO")
            PlayBoll=True
        else:
            Stop()
    def getContext():
        con=context_text.get()
        return con.replace("|","\n")
    def tredLog(file):
        toMidGa.start("file.mid")
        gits("")
        noteInstEv("")
    def playEntr(e):
        command=":"+str(tempo)+";"+str(midinote)+"\n"
        command+="same\n"
        command+=getContext()+"\n"
        command+=entry_text.get()+"\n"
        command+="end:note\n"
        command+="add('note')\n"
        print(command)
        gits("")
        toMidiMeth.toMidi("file",0,MIDIFile(1),line=command,fromStr=True)
        streml=threading.Thread(target=tredLog,args=("file.mid",),daemon=True)
        streml.start()
    def upDateRecreate():
        nonlocal recrateBool,poseObjVect,intPoseK

        #recreateBool=True
        poseL=[int(PoseChords[0]),int(PoseChords[1]),int(PoseChords[2])]
      #  poseObjVect=[ObjPose[0]-PoseChords[0],ObjPose[1]-PoseChords[1],ObjPose[2]-PoseChords[2]]
        print(poseObjVect)
        if([int(intPoseK[0]),int(intPoseK[1]),int(intPoseK[2])]!=poseL):
            intPoseK=PoseChords.copy()
           # print([int(PoseChords[0]+poseObjVect[0]-1),int(PoseChords[1]+poseObjVect[1]-1),int(PoseChords[2]+poseObjVect[2]-1)])
            createObjects(Range,poseChords=[int(PoseChords[0]+poseObjVect[0]),int(PoseChords[1]+poseObjVect[1]),int(PoseChords[2]+poseObjVect[2])])
        ##
    def startPlayBind(ev):
        print(path+"/"+file)
        startPlay([path+"/"+file])
    def DrewLines(e):
        nonlocal EnabeLines
        EnabeLines=not EnabeLines
        checkL.set(EnabeLines)
        if(not EnabeLines):
            canvas.itemconfigure("line", state='hidden')
        else:
            canvas.itemconfigure("line", state='normal')
    def DirChange(ev):
        nonlocal directions
        USER_INP = simpledialog.askstring(title="ПК",
                                          prompt="Измените пространство кратностей\nВведите целые числа через пробел")
        spl=USER_INP.split(" ")
        ints=[]
        for s in spl:
            if(s!=""):
                ints.append(int(s))
        directions=ints
    def DirCount(ev):
        nonlocal dirCnt
        USER_INP = simpledialog.askstring(title="куб",
                                          prompt="Колово измерений куба")
        dirCnt=int(USER_INP)
    def rangeDir(ev):
        nonlocal Range
        USER_INP = simpledialog.askstring(title="куб",
                                          prompt="Точек куба")
        Range=int(USER_INP)
    def chordEntr():
        chord.set(str(int(PoseChords[0]))+" "+str(int(PoseChords[1]))+" "+str(int(PoseChords[2])))
        chordObj.set(str(int(ObjPose[0]))+" "+str(int(ObjPose[1]))+" "+str(int(ObjPose[2])))

    def Manual(e):
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
    def setBol():
        nonlocal recrateBool,EnabeLines
        if(checkOt.get()!=recrateBool):
            rgrecrate1("")
        if(EnabeLines!=checkL.get()):
            DrewLines("")
       # recrateBool=checkOt.get()
       #EnabeLines=checkL.get()
    def upDateCube(ev):
        createObjects(Range,dir=dirCnt,poseChords=ObjPose)
    def arrayMonitoring():
        nonlocal path,file,array
        while True:
            h=open("playInf.txt","r")
            p=h.readline().split(":")
            h.close()
           # print(p)
            if(p[0]=="play"):
                if(not PlayBoll):
                     st=threading.Thread(target=startPlay,args=(p[1].split(" "),),daemon=True)
                     st.start()
                with open("playInf.txt", "w") as f:
                    f.write("none")
            if(p[0]=="stop"):
                Stop()
                with open("playInf.txt", "w") as f:
                    f.write("none")
          #  print(array)
         #   if(len(array)>0):
              #  if(array[0]=="play"):
                  #  st=threading.Thread(target=startPlay,args=(array[1],),daemon=True)
                  #  st.start()
                  #  array=[]
           #     if(array[0]=="stop"):
                  #  Stop()
            time.sleep(arrayRate*5)
          #  canvas.delete("line")
   # def UpDir()
    createObjects(Range,dir=dirCnt,poseChords=[0,0,0])
    canvas.bind('<ButtonPress-1>', click)
    canvas.bind('<Alt-KeyPress-f>', changeCurs)
    canvas.bind('<Alt-KeyPress-g>', enabeWASD)
    canvas.bind('<Control-KeyPress-f>', DirChange)

    canvas.bind('<F1>', playEntr)
    canvas.bind('<Control-KeyPress-c>', copy)

    canvas.bind('<KeyPress-h>', DirCount)
    canvas.bind('<KeyPress-y>', rangeDir)
    canvas.bind('<KeyPress-q>', objectRecreate)
    canvas.bind('<KeyPress-m>', Manual)
    #canvas.bind('<KeyPress-p>', rgrecrate1)
    #canvas.bind('<KeyPress-p>', startPlayBind)
    canvas.bind('<KeyPress-e>', Enabe)
    canvas.bind('<KeyPress-r>', clearEntr)
    canvas.bind('<KeyPress-t>', tp0)
    canvas.bind('<KeyPress-b>', backSpace)
    canvas.bind('<KeyPress-l>', DrewLines)
    canvas.bind('<KeyPress-o>', rgrecrate1)
    canvas.bind('<KeyPress-u>', upDateCube)

    allFrame.bind('<FocusIn>',noteInstEv)
    allFrame.bind('<FocusOut>',gits)

  #  print(array)
   # array.append(startPlay)
    manual = tk.Label(allFrame, text="инструкция - m(маленькая/англ)")
  #  label = tk.Label(allFrame, text="change mouse function - Alt+F")
  #  label1 = tk.Label(allFrame, text="change WASD function - Alt+G")
    label3 = tk.Label(allFrame, text="context")
  #  label.pack()
  #  label1.pack()
    manual.pack()
    canvas.pack(anchor=CENTER)
    FrameStats.pack(anchor=E)
    context_entry.pack()
    label3.pack()
    entry.pack()
    EntryBox.pack(anchor=CENTER)
    movetread =threading.Thread(target=move,daemon = True)
    arrayTr=threading.Thread(target=arrayMonitoring,daemon=True)
    sort =threading.Thread(target=mnSort,daemon = True)
    sort.start()
    allFrame.grid(row = 0, column = 11,columnspan=5,rowspan=4)
    movetread.start()
    arrayTr.start()

#root =tk.Tk()
#canvasS(root,path="music/visual",file="chord(visual).txt",winStats="450x450+600+300")

#root.mainloop()