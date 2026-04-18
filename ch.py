import math,re

defSimpNum=[2,3,5,7,11,13,17,19,23]
centConst=math.pow(2,1/1200)
special=["c",'f','e']

def transit(chords, dir1, dir2):
    dictO={}
    chds=[]
    for i in range(len(dir1)):
        if(i<len(chords)):
            dictO[dir1[i]]=chords[i]
        else:
            dictO[dir1[i]]=0
    cnt=0
    for i in range(len(dir2)):
        if(dictO.get(dir2[i])!=None):
            chds.append(dictO.get(dir2[i]))
            cnt+=1
        else:
            chds.append(0)
        if(cnt==len(chords)):
            break
    return chds


def readConfig(file):
    f=open(file,"r")
    line=f.readlines()
    massL=[]
    for i in range(len(line)):
        vect=[]
        if(line[i]!=""):
            pr=line[i].split(" ")
            for m in range(3):
                vect.append(float(pr[m]))
            lenS=math.pow(math.pow(vect[0],2)+math.pow(vect[1],2)+math.pow(vect[2],2),1/2)
            for m in range(3):
                vect[m]=vect[m]/lenS
            massL.append(vect)
    return massL

def toVect(chords,config,**kwargs):
    start=kwargs.get("start",0)
    vect=[0,0,0]
    for i in range(len(chords)):
        vect[0]+=config[i+start][0]*chords[i]
        vect[1]+=config[i+start][1]*chords[i]
        vect[2]+=config[i+start][2]*chords[i]
    return vect
def numToChord(num,simpleNumbers):
    a=num
    mass=[]
    itog=[]
    max=0
    for i in range(len(simpleNumbers)):
        cnt=0
        while a%simpleNumbers[i]==0:
            a=a//simpleNumbers[i]
            cnt+=1
        if(cnt!=0):
            max=i
        mass.append(cnt)
    for i in range(max):
        itog.append(mass[i+1])
    return itog

def chordStr(chord,**kwargs):
    oct=kwargs.get("oct",0)
    conLen=kwargs.get("conLen","false")
    lenS=kwargs.get("len",conLen)
    contextVel=kwargs.get("conVel",-1)
    vel=kwargs.get("vel",contextVel)
    strn=""
    max=0
    for i in range(len(chord)):
        if(chord[i]!=0):
            max=i
    for i in range(max+1):
        strn+="."+str(chord[i])
    if(oct!=0):
        if(oct==1):
            strn+="+"
        else:
            if(oct==-1):
                strn+="-"
            else:
                strn+=str(oct)
    if(lenS!=conLen):
        strn+=":"+lenS
    if(contextVel!=vel):
        strn+="v"+vel
    return strn[1:]
def toFrame(framerate,tempo,timeInBeats):
    tmpC=60/tempo
    time=timeInBeats*tmpC
    return int(time/(1/framerate))
def fcentSplit(fc):
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
    return str
def vector(fc,config,edo):
   # print(centConst,defSimpNum[1],const)
    if("c" in fc):
      #  print(fc)
        const=math.log(defSimpNum[1],centConst)
        print(fc)
        print(centConst,defSimpNum[1],const)
        print([0,int(fc.replace("c",""))/const,0])
        return [0,int(fc.replace("c",""))/const,0]
    if("с" in fc):
        #  print(fc)
        const=math.log(defSimpNum[1],centConst)
        print(centConst,defSimpNum[1],const)
        #  print([0,int(fc.replace("c",""))/const,0])
        return [0,int(fc.replace("с",""))/const,0]
    if("f" in fc):
        return toVect(numToChord(int(fc.replace("f","")),defSimpNum),config)
    if("e" in fc):
        const=math.log(defSimpNum[1],centConst)
        note=math.log(math.pow(math.pow(defSimpNum[0],1/edo),int(fc.replace("e",""))),centConst)
        return [0,int(note/const),0]
    vct=fc.split(".")
    vect=[]
    for i in range(len(vct)):
        vect.append(int(vct[i]))
    return toVect(vect,config)
def intChordMass(list):
    p=list[0]
   # print(list)
    if(len(list)>2):
        for i in range(len(list)-2):
            p=intChordStr(p,list[i+1])
    return intChord(p,list[len(list)-1])
def VectFcent(list,config,**kwargs):
    edo=kwargs.get("edo",12)
    vectors=[]
    for cho in list:
        vectors.append(vector(fcentSplit(cho),config,edo))
    vect=[0,0,0]
    for cho in vectors:
        for i in range(3):
            vect[i]+=cho[i]
    return vect
def notSpec(note):
    for c in special:
        if c in note:
            return False
    return True
def setOct(num):
    return num*math.pow(defSimpNum[0],1)
def cents(num):
    return int(math.log(num,centConst))
def midipith(cents):
    return [cents//100,cents%100]
def toPith(cnt):
    return 8192/200*cnt
def fromEdo(step,EDOconst):
    return math.pow(EDOconst,step)
def getNum(nump):
    m=nump.split(".")
    intA=1
    for i in range(len(m)):
        intA=intA*math.pow(defSimpNum[1+i],int(m[i]))
    return intA
def tPose(num):
    j=num
    #  p=tPoseRot(getNum(rootm))
    while(j>defSimpNum[0]):
        j=j/defSimpNum[0]
    while(j<1):
        j=j*defSimpNum[0]
    return j
def fcent2(fc,edo):
    if "f" in fc:
        return cents(float(fc.replace("f","")))
    if "c" in fc:
        return int(fc.replace("c",""))
    if "с" in fc:
        return int(fc.replace("с",""))
    if "e" in fc:
        return cents(fromEdo(float(fc.replace("e",""))))
    return cents(setOct(tPose(getNum(fc))))
def intChordStr(root,r):
    rootm=fcentSplit(root)
    if(rootm=="?" or r=="?"):
        return "?"
    dtr=fcentSplit(r)
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
        return strK
    else:
        return "?"
def intChord(rot,r):
    rootm=fcentSplit(rot)
    if(rootm=="?" or r=="?"):
        return "?"
    dtr=fcentSplit(r)
    if(notSpec(rootm) and notSpec(r)):
        nm1=dtr.split(".")
        nm2=rootm.split(".")
        jk=max(len(nm1),len(nm2))
        lMas=[]
        for i in range(jk):
            c=0
            if(i<len(nm1)):
                c+=int(nm1[i])
            if(i<len(nm2)):
                c+=int(nm2[i])
            lMas.append(c)
        return lMas
    return "?"
def r(mass):
    m=[]
    for i in range(len(mass)-1):
        m.append(mass[i+1])
    return m
print(numToChord(55*13*9,defSimpNum))
print(chordStr([1]))