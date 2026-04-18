import re
import time
from pygments.styles import get_style_by_name
import tkinter.font as tkFont
import pygments.token as tok
import tkinter as tk
from pygments.token import *
from src.MuzCube.UtilFIles import dataTok
import MuzCubeLexer


def getIntBools(params):
    split = params.split(" ")
    i1=-1
    i2=-1
    for i in range(len(split)):
        if split[i]=="bold":
            i1=1
        elif split[i]=="italic":
            i2=1
        elif split[i]=="nobold":
            i1=0
        elif split[i]=="noitalic":
            i2=0
    return [i1,i2]

def getState(string,strNum):
    spl=string.split("\n")
    i=strNum-1
    while i>0:
        if re.match(r"same",spl[i]):
            return 'inSame'
        elif re.match(r"end[ \t]*:",spl[i]):
            return 'root'
        i-=1
    return 'root'

def get_text_coord(s: str, i: int):
    for row_number, line in enumerate(s.splitlines(keepends=True), 1):
        if i < len(line):
            return f'{row_number}.{i}'

        i -= len(line)
def get_text_coordXY(s: str, i: int,y,x):
    for row_number, line in enumerate(s.splitlines(keepends=True), 1):
        if i <= len(line):
            return f'{row_number+y}.{i+x}'

        i -= len(line)
def getType(token_type):
    if(token_type is tok.Token):
        return "tok"
    elif (token_type is tok.Token.Text):
        return "tx"
    else:
        return tok.STANDARD_TYPES[token_type]
class ColoredTkinter:
    def __init__(self,fontName,fontSize,styleName,**kwargs):
        self.rateUpdate=kwargs.get('rateUpdate',1)
        #   self.textBox=textBox
        self.boxes=[]
        self.binds=[]
        self.fontName=fontName
        self.fontSize=fontSize
        self.styleName=styleName
        self.token_to_tag={}
        self.masTags=[]
        self.colors ={}
        self.lexer=kwargs.get('lexer',MuzCubeLexer.MuzCubeLexer())
    # self.configureTextBox(self.masTags,self.textBox,self.fontName,self.fontSize,self.styleName,self.token_to_tag)

    #   self.textBox.bind('<<Modified>>', self.on_edit)
    def createTag(self,textBox,name,params,fontName,fontSize,**kwargs):
        if(params==""):
            return
        intBool=kwargs.get("parrentBool",None)
        style=kwargs.get("style",None)
        split = params.split(" ")
        bold=False
        italic=False
        if(intBool is not None):
            if(intBool[0]==1):
                bold=True
            if(intBool[1]==1):
                italic=True
        for i in range(len(split)):
            if(split[i]!=""):
                if split[i][0]=="#":
                    textBox.tag_config(name,foreground=split[i])
                    self.colors[name]=split[i]
                else:
                    if ":" in split[i]:
                        sc=split[i].split(":")
                        if sc[0] == "bg":
                            if(sc[1]!=""):
                                textBox.tag_config(name,background=sc[1])
                            else:
                                textBox.tag_config(name,background=style.background_color)
                        elif sc[0] == "border":
                            if(sc[1]!=""):
                                textBox.tag_config(name,border=sc[1])
                    else:
                        if split[i]=="bold":
                            bold=True
                        elif split[i]=="nobold":
                            bold=False
                        elif split[i]=="italic":
                            italic=True
                        elif split[i]=="noitalic":
                            italic=False
                        elif split[i]=="underline":
                            textBox.tag_config(name,underline=True)
                        elif split[i]=="nounderline":
                            textBox.tag_config(name,underline=False)
        if(bold and italic):
            textBox.tag_config(name,font=tkFont.Font(family=fontName,size=int(fontSize),weight=tkFont.BOLD, slant=tkFont.ITALIC))
        elif(bold):
            textBox.tag_config(name,font=(fontName,fontSize,"bold"))
        elif(italic):
            textBox.tag_config(name,font=(fontName,fontSize,"italic"))
    def getColor(self,token_type):
        if getType(token_type) in self.colors:
            return self.colors.get(getType(token_type))
        else:
            mas= dataTok.STANDARD_TYPES_SP[token_type]
            ln=len(dataTok.STANDARD_TYPES_SP[token_type])
            c=1
            for k in range(len(mas)-1):
                if(dataTok.STANDARD_TYPES_SP[token_type][ln - c] in self.colors):
                    return self.colors.get(dataTok.STANDARD_TYPES_SP[token_type][ln - c])
                c+=1
            if(c==ln):
                return self.colors.get("tok")
    def getConfigLines4(self):
        return [self.getColor(Keyword),self.getColor(Name.Function),self.getColor(Name.Class),self.getColor(Name.Builtin)]
    def reColor(self,styleName):
        self.styleName=styleName
        for text in self.boxes:
            self.configureTextBox(self.masTags,text,self.fontName,self.fontSize,self.styleName,self.token_to_tag)
    def addTextBox(self,textBox):
        self.masTags=[]
        self.boxes.append(textBox)
        self.configureTextBox(self.masTags,textBox,self.fontName,self.fontSize,self.styleName,self.token_to_tag)
        self.binds.append(BindColor(textBox,self))
    def removeTextBox(self,textBox):
        # textBox.unbind('<<Modified>>')
        for i in range (len(self.boxes)):
            if textBox == self.boxes[i]:
                self.boxes.remove(textBox)
                self.binds.pop(i)
                break
    # def self.event
    def configureTextBox(self,masTags,textBox,fontName,fontSize,styleName,token_to_tag):
        style=get_style_by_name(styleName)
        textBox.config(font=(fontName,fontSize),background=style.background_color,selectbackground=style.highlight_color)
        dictBase={}
        dictIntBools={}
        ct=0
        for token, params in style.styles.items():
            if(tok.STANDARD_TYPES.get(token,None) is not None):
                dictBase[getType(token)]=params
                dictIntBools[getType(token)]=getIntBools(params)
                masTags.append(getType(token))
        for token, params in style.styles.items():
            if(tok.STANDARD_TYPES.get(token,None) is not None):
                token_to_tag[token]=getType(token)
                ct2= len(dataTok.STANDARD_TYPES_SP[token]) - 1
                while(ct2>0 and not "noinherit" in dictBase[dataTok.STANDARD_TYPES_SP[token][ct2]]):
                    ct2-=1
                ct3=ct2
                while(ct2<len(dataTok.STANDARD_TYPES_SP[token])):
                    if(ct2==ct3):
                        self.createTag(textBox, getType(token), dictBase[dataTok.STANDARD_TYPES_SP[token][ct2]], fontName, fontSize, style=style)
                    else:
                        if(dictBase.get(dataTok.STANDARD_TYPES_SP[token][ct3], None) is not None):
                            self.createTag(textBox, getType(token),
                                           dictBase[dataTok.STANDARD_TYPES_SP[token][ct2]], fontName, fontSize, style=style,
                                           parrentBool=dictIntBools[dataTok.STANDARD_TYPES_SP[token][ct3]])
                        ct3+=1
                    ct2+=1
                ct+=1
        textBox.config(insertbackground=self.getColor(Name))
    def configureTextBox2(self,masTags,textBox,fontName,fontSize,styleName,token_to_tag):
        style=get_style_by_name(styleName)
        textBox.config(font=(fontName,fontSize),background=style.background_color,selectbackground=style.highlight_color)
        dictBase={}
        dictBase2={}
        dictIntBools={}
        ct=0

        for token, params in style.styles.items():
            if(tok.STANDARD_TYPES.get(token,None) is not None):
                dictBase[getType(token)]=params
                dictIntBools[getType(token)]=getIntBools(params)
                masTags.append(getType(token))

        for token, params in style.styles.items():
            dictBase2[token]=params
        for token, name in tok.STANDARD_TYPES:
            if dictBase2.get(token, None) is None:
                parent = token
                while parent.parent is not None:
                    parent = parent.parent
                    if dictBase2.get(parent, None) is not None:
                        dictBase2[token] = dictBase2.get(parent)
                        break

        for token, params in style.styles.items():
            if(tok.STANDARD_TYPES.get(token,None) is not None):
                token_to_tag[token]=getType(token)
                ct2= len(dataTok.STANDARD_TYPES_SP[token]) - 1
                while(ct2>0 and not "noinherit" in dictBase[dataTok.STANDARD_TYPES_SP[token][ct2]]):
                    ct2-=1
                ct3=ct2
                while(ct2<len(dataTok.STANDARD_TYPES_SP[token])):
                    if(ct2==ct3):
                        self.createTag(textBox, str(token), dictBase[dataTok.STANDARD_TYPES_SP[token][ct2]], fontName, fontSize, style=style)
                    else:
                        if(dictBase.get(dataTok.STANDARD_TYPES_SP[token][ct3], None) is not None):
                            self.createTag(textBox, str(token),
                                           dictBase[dataTok.STANDARD_TYPES_SP[token][ct2]], fontName, fontSize, style=style,
                                           parrentBool=dictIntBools[dataTok.STANDARD_TYPES_SP[token][ct3]])
                        ct3+=1
                    ct2+=1
                ct+=1
        textBox.config(insertbackground=self.getColor(Name))

        textBox.config(insertbackground=self.getColor(Name))



class BindColor:
    def __init__(self,textBox,base):
        self.textBox=textBox
        self.base=base
        self.lightModify=0
        self.rate=1
        # self.on_edit("")
        # textBox.bind('<<Modified>>',self.lightEdit)
        #   textBox.bind('<<Modified>>',self.modifi)
        #  self.upThread=Thread(target=self.modifiThread,daemon=True)
        #   self.upThread.start()
        textBox.bind('<<Modified>>', self.on_edit)
    def modifiThread(self):
        if self.lightModify == 1:
            self.lightEdit("")
            self.lightModify=0
            time.sleep(self.rate)
    def update(self,s,**kwargs):
        Y=kwargs.get("Y",0)
        X=kwargs.get("X",0)
        state=kwargs.get("state",'root')
        #        tokens = self.base.lexer.get_tokens_unprocessed(s, stack=(state,))
        tokens = self.base.lexer.get_tokens_unprocessed(s)
        #  self.base.lexer.get_tokens_unprocessed(s)
        for i, token_type, token in tokens:
            if(dataTok.STANDARD_TYPES_SP.get(token_type, None) is not None):
                j = i + len(token)
                mas= dataTok.STANDARD_TYPES_SP[token_type]
                ln=len(dataTok.STANDARD_TYPES_SP[token_type])
                si=get_text_coordXY(s, i,Y,X)
                sj=get_text_coordXY(s, j,Y,X)
                c=1
                if token_type in self.base.token_to_tag:
                    self.textBox.tag_add(self.base.token_to_tag[token_type], si, sj)
                else:
                    for k in range(len(mas)-1):
                        if dataTok.STANDARD_TYPES_SP[token_type][ln - c] in self.base.masTags:
                            self.textBox.tag_add(dataTok.STANDARD_TYPES_SP[token_type][ln - c], si, sj)
                            break
                        c+=1
                    if(c==ln):
                        self.textBox.tag_add("tok", si, sj)
        self.textBox.edit_modified(0)
    def on_edit(self,event):
        # Удалить все имеющиеся теги из текста
        for tag in self.textBox.tag_names():
            self.textBox.tag_remove(tag, 1.0, tk.END)
        # Разобрать текст на токены
        s = self.textBox.get(1.0, tk.END)
        self.update(s)
    def modifi(self,event):
        self.lightModify=1
    def lightEdit(self,event):
        num = self.textBox.index(tk.INSERT)
        splNum=num.split(".")
        stNum=f'{splNum[0]}.{0}'
        for tag in self.textBox.tag_names():
            self.textBox.tag_remove(tag,stNum, num)
        s = self.textBox.get(stNum, num)
        state=getState(self.textBox.get(1.0, tk.END),int(splNum[0])-1)
        self.update(s,Y=int(splNum[0])-1,X=0,state=state)








