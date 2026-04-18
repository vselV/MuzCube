import math
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