import math
import re
simpleNumbers=[2,3,5,7,11,13,17,19,23]
oneCent=math.pow(2,1/1200)
octave=2
def getNum(nump):
    m=nump.split(".")
    intA=1
    for i in range(len(m)):
        intA=intA*math.pow(simpleNumbers[1+i],int(m[i]))
    return intA
def setOct(num):
    return num*math.pow(simpleNumbers[0],octave)
def tPose(num):
    j=num
    while(j>simpleNumbers[0]):
        j=j/simpleNumbers[0]
    while(j<1):
        j=j*simpleNumbers[0]
    return j
def cents(num):
    return math.log(num,oneCent)
def midipith2(cents):
    return [cents//100,cents%100]
def midipith(cents):
    num=int(cents)//100
    return [num,cents-num*100]
def toPith(cnt):
    return 8192/200*cnt
def outPitch(mid):
    return [mid[0],int(toPith(mid[1]))]

def fcent(fc):
    if "f" in fc:
        return cents(float(fc.replace("f","")))
    if "c" in fc:
        return int(fc.replace("c",""))
    return cents(setOct(tPose(getNum(fc))))
def fcent(fc):
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
def fcentOct(fc):
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
def interPr(lin):
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