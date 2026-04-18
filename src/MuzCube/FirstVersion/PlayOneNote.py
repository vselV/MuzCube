import math
import pygame.midi
import time

player = ""
actnote=0
chanel=0
itstI=False
def init(intst):
    global itstI,player
    if(not itstI):
        try:
            pygame.midi.init()
            itstI=True
            player = pygame.midi.Output(0)
            player.set_instrument(intst)
        except:
            itstI=False
            print(intst,player)

def PlayNote(timeS,midinote,note,tempo,programm,oct,root,vel,simpleNum):
    player.set_instrument(programm)
    global actnote,chanel,itstI
    if(not itstI):
        init(0)
    octave=oct
    simpleNumbers=simpleNum
    oneCent=math.pow(2,1/1200)
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
        return int(math.log(num,oneCent))
    def midipith(cents):
        return [cents//100,cents%100]
    def toPith(cnt):
        return 8192/200*cnt
    def fcent(fc):
        if "f" in fc:
            return cents(float(fc.replace("f","")))
        if "c" in fc:
            return int(fc.replace("c",""))
        return cents(setOct(tPose(getNum(fc))))
    nOne=fcent(note)+fcent(root)
    nRoot=midipith(nOne)
    actnote=midinote
    if(chanel%16==9):
        chanel+=1
    player.note_on(midinote+nRoot[0], vel,chanel%16)
    player.pitch_bend(int(toPith(nRoot[1])),chanel%16)
    bk=chanel
    chanel+=1
    time.sleep(4)
    if(itstI):
        player.note_off(midinote+nRoot[0], vel,bk%16)
def qit():
    global itstI
    if(itstI):
        try:
            pygame.midi.quit()
            itstI=False
        except:
            itstI=True
