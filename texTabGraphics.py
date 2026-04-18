import tkinter as tk
from tkinter import ttk
import tkinter.filedialog
from tkinter import messagebox
from midiutil import MIDIFile
from tkinter import simpledialog
import os
from hashlib import md5
import re
import threading
import time
import tkinter.font
import tkinter.font as tkFont
from src.MuzCube.Scripts import allMidiFrom, createMidi
import toMidiMeth
import src.MuzCube.FirstVersion.toMidGa
import GraphTestForTab
import src.MuzCube.FirstVersion.GaInit
from src.MuzCube.UtilClasses import colorClass
from pygments.styles import get_style_by_name

allCommands=[["root","oct","inst","vel","edo","valOct","chan","reLen","setScale"],["add","SM"],["same"],["end"],["load","swap"],["chord","pattern","scale","arpeg"],["fix","turn","tp","getState","setState","unBind","noteBind"]]
SetCommands=["root","oct","inst","vel"]
Add=["add"]
Same=["same"]
End=["end"]
colos =["e5a45a","9470c2","5a71e5","e55a5a"]
colosTk =["green4","SlateBlue","DodgerBlue3","firebrick3","darkorange4","deeppink4","midnightblue"]
selectColor="burlywood1"
#colosTk =["darkgoldenrod2","darkslateblue","deeppink3","firebrick3"]
rate=0.5
fontName="Segoe UI"
fontSize=12

class Notebook(ttk.Notebook):
    def __init__(self, *args):
        ttk.Notebook.__init__(self, *args,width=550)
        self.enable_traversal()
      #  self.pack(expand=1, fill="both")
       # self.pack(anchor=W)
        self.grid(row = 0, column = 0,columnspan=5)
        self.bind("<B1-Motion>", self.move_tab)
        self.start = threading.Thread(target=self.regularUpdate,daemon = True)
        #self.start.start()

    # Get the object of the current tab.
    def startUpdate(self):
        self.start.start()
    def current_tab(self):
        return self.nametowidget( self.select() )

    def indexed_tab(self, index):
        return self.nametowidget( self.tabs()[index] )
    def len(self):
        return len(self.tabs())
    def regularUpdate(self):
        global rate

        while True:
         #   print(self.focus_get())
            #    print(self.fo)
            #   print(self.sele)
            self.current_tab().uppdateColors()
            time.sleep(rate)
    # Move tab position by dragging tab
    def move_tab(self, event):
        '''
        Check if there is more than one tab.

        Use the y-coordinate of the current tab so that if the user moves the mouse up / down
        out of the range of the tabs, the left / right movement still moves the tab.
        '''
        if self.index("end") > 1:
            y = self.current_tab().winfo_y() - 5

            try:
                self.insert( min( event.widget.index('@%d,%d' % (event.x, y)), self.index('end')-2), self.select() )
            except tk.TclError:
                pass

class Tab(ttk.Frame):
    def regularUpdate(self):
        global rate

        while True:
            print(self.focus_get())
        #    print(self.fo)
         #   print(self.sele)
            if(self.focus_get()):
                self.uppdateColors()
            time.sleep(10*rate)
    def getFileDir(self):
        return self.file_dir
    def __init__(self, *args, FileDir):
        default_font = tkFont.nametofont("TkFixedFont")
        default_font.configure(family=fontName,size=fontSize)
        print(FileDir)

        ttk.Frame.__init__(self, *args,width=465)
        self.textbox = self.create_text_widget()
        self.file_dir = FileDir
        self.file_name = os.path.basename(FileDir)
        self.status = md5(self.textbox.get(1.0, 'end').encode('utf-8'))
        self.count=0
        self.massChord=[]
        self.dictO={}
        font=tkinter.font.Font( family = fontName,
                                size = fontSize)
        self.fontT = tkinter.font.Font(self.textbox, font)
        self.fontT.configure()
        for a in range(len(colosTk)):
            for b in range(len(allCommands[a])):
                self.textbox.tag_configure("tag_color_txt"+str(a)+"#"+str(b), font=self.fontT, foreground=colosTk[a])
    def getTextBox(self):
        return self.textbox



    def uppdateColors(self):
        # create
        global allCommands,colosTk
        lP=int(self.textbox.index('end-1c').split('.')[0])
        for a in range(len(colosTk)):
            for b in range(len(allCommands[a])):
                l=len(allCommands[a][b])
                for i in range(lP):
                    k=i+1
                    if(i==lP-1):
                        k=i
                    s=self.textbox.search(allCommands[a][b],str(i)+".0",str(k)+".0")
                    if(s==""):
                        self.textbox.tag_remove("tag_color_txt"+str(a)+"#"+str(b),str(i)+".0",str(k)+".0")
                        continue
                    s2=s.split(".")[0]+"."+str(int(s.split(".")[1])+int(l))
                    self.textbox.tag_remove("tag_color_txt"+str(a)+"#"+str(b),str(i)+".0",str(k)+".0")
                    self.textbox.tag_add("tag_color_txt"+str(a)+"#"+str(b), s, s2)
    def create_text_widget(self):
        global selectColor
        # Horizontal Scroll Bar
        xscrollbar = tk.Scrollbar(self, orient='horizontal')
        xscrollbar.pack(side='bottom', fill='x')

        # Vertical Scroll Bar
        yscrollbar = tk.Scrollbar(self)
        yscrollbar.pack(side='right', fill='y')

        # Create Text Editor Box
        textbox = tk.Text(self, relief='sunken', borderwidth=0, wrap='none')
        textbox.config(xscrollcommand=xscrollbar.set, yscrollcommand=yscrollbar.set, undo=True, autoseparators=True,selectbackground=selectColor,selectforeground="black")

        # Pack the textbox
        textbox.pack(fill='both', expand=True)
       # textbox.pack()
        # Configure Scrollbars
        xscrollbar.config(command=textbox.xview)
        yscrollbar.config(command=textbox.yview)

        return textbox

class Editor:
    def __init__(self, master,mypath,**kwargs):
        self.style=kwargs.get("style",None)
        self.Colored=None
        self.styleFromName=None
        if(self.style is not None):
            self.Colored= colorClass.ColoredTkinter("Courier", "12", self.style)
            self.styleFromName=get_style_by_name(self.style)
        self.graph=kwargs.get("graph",None)

        self.mypath=mypath
        self.files= allMidiFrom.allMidi(mypath)

        self.Graphics=""
        self.arrayLink=""

        self.master = master
        self.master.title("Notepad+=1")
        self.frame = tk.Frame(self.master)
###
        self.filetypes = (("Normal text file", "*.txt"), ("all files", "*.*"))
        self.init_dir = os.path.join(os.path.expanduser('~'), 'Desktop')
        self.untitled_count = 1

        # Create Notebook ( for tabs ).
        self.nb = Notebook(master)
        self.nb.bind("<Button-2>", self.close_tab)
        self.nb.bind('<<NotebookTabChanged>>', self.tab_change)
        self.nb.bind('<Button-3>', self.right_click_tab)

        # Override the X button.
        self.master.protocol('WM_DELETE_WINDOW', self.exit)

        # Create Menu Bar
        menubar = tk.Menu(self.master)

        # Create File Menu
        filemenu = tk.Menu(menubar, tearoff=0)
        filemenu.add_command(label="New", command=self.new_file)
        filemenu.add_command(label="Open", command=self.open_file)
        filemenu.add_command(label="Save", command=self.save_file)
        filemenu.add_command(label="Save As...", command=self.save_as)
        filemenu.add_command(label="Close", command=self.close_tab)
        filemenu.add_separator()
        filemenu.add_command(label="Delete File", command=self.deliteFileInTab)
        filemenu.add_separator()
        filemenu.add_command(label="Exit", command=self.exit)

        # Create Edit Menu
        editmenu = tk.Menu(menubar, tearoff=0)
        editmenu.add_command(label="Undo", command=self.undo)
        editmenu.add_separator()
        editmenu.add_command(label="Cut", command=self.cut)
        editmenu.add_command(label="Copy", command=self.copy)
        editmenu.add_command(label="Paste", command=self.paste)
        editmenu.add_command(label="Delete", command=self.delete)
        editmenu.add_command(label="Select All", command=self.select_all)
        editmenu.add_command(label="Delete File", command=self.deliteFileInTab)
        # Create Format Menu, with a check button for word wrap.
        formatmenu = tk.Menu(menubar, tearoff=0)
        self.word_wrap = tk.BooleanVar()
        formatmenu.add_checkbutton(label="Word Wrap", onvalue=True, offvalue=False, variable=self.word_wrap, command=self.wrap)

        # Attach to Menu Bar
        menubar.add_cascade(label="File", menu=filemenu)
        menubar.add_cascade(label="Edit", menu=editmenu)
        menubar.add_cascade(label="Format", menu=formatmenu)
        self.master.config(menu=menubar)

        # Create right-click menu.
        self.right_click_menu = tk.Menu(self.master, tearoff=0)
        self.right_click_menu.add_command(label="Undo", command=self.undo)
        self.right_click_menu.add_separator()
        self.right_click_menu.add_command(label="Cut", command=self.cut)
        self.right_click_menu.add_command(label="Copy", command=self.copy)
        self.right_click_menu.add_command(label="Paste", command=self.paste)
        self.right_click_menu.add_command(label="Delete", command=self.delete)
        self.right_click_menu.add_separator()
        self.right_click_menu.add_command(label="Select All", command=self.select_all)


        # Create tab right-click menu
        self.tab_right_click_menu = tk.Menu(self.nb, tearoff=0)
        self.tab_right_click_menu.add_command(label="New Tab", command=self.new_file)
        self.BolPlay=tk.BooleanVar(value=False)
        self.PlayBox = ttk.Checkbutton(master,text="visual", variable=self.BolPlay)

        # Keyboard / Click Bindings
        self.master.bind_class('Text', '<Control-s>', self.save_file)
        self.master.bind_class('Text', '<Control-o>', self.open_file)
        self.master.bind_class('Text', '<Control-n>', self.new_file)
        self.master.bind_class('Text', '<Control-a>', self.select_all)
        self.master.bind_class('Text', '<Control-w>', self.close_tab)
        self.master.bind_class('Text', '<Button-3>', self.right_click)
        master.bind_class('Text', '<F1>', self.runSelected)
        #self.nb.add(Tab(FileDir='Untitled'), text='Untitled')

        #BUTTON
        self.btn = ttk.Button(text="Run Current", command=self.runCurrent)
        self.btn.grid(row=1,column=1,columnspan=1)
        self.btn2 = ttk.Button(text="Run All", command=self.runAll)
        self.btn2.grid(row=1,column=2,columnspan=1)


        self.entry_text = tk.StringVar()
        self.entry = tk.Entry( master, textvariable=self.entry_text ,bg="grey87",fg="NavyBlue", width=40)
        self.entry.grid(row=2,column=0,columnspan=5)

        self.lable=tk.Label(master,text="F1 - Run Selected")
        self.lable.grid(row=3,column=0,columnspan=5)
        self.PlayBox.grid(row=4,column=0)
        label=tk.Label(master,text="<< - работает очень плохо   :(")
        label.grid(row=4,column=1,columnspan=2)

        self.nb.add(Tab(FileDir='f'), text=' + ')
        for i in range(len(self.files)):
            self.open_fileFromDir(self.mypath+"/"+self.files[i])
        # Create initial tab and 'Add' tab
        self.saveTr=threading.Thread(target=self.regularSave,daemon=True)
        self.saveTr.start()
        if(self.style is not None):
            # self.recolor(self.style)
            self.addTabs()
           # self.colorOther()
        else:
            self.nb.startUpdate()
    def colorOther(self):
        if(self.styleFromName is not None):
            self.master.configure(background=self.styleFromName.background_color)
          #  self.master.config(background)
    def recolor(self,styleName):
        if(self.Colored is not None):
            self.Colored.reColor(styleName)
    def addTabs(self):
        if(self.Colored is not None):
            for i in range( self.nb.index('end')-1):
                self.Colored.addTextBox(self.nb.indexed_tab(i).getTextBox())
    def addTabCol(self,textBox):
        if(self.Colored is not None):
            self.Colored.addTextBox(textBox)
    def removeTabCol(self,textBox):
        if(self.Colored is not None):
            self.Colored.removeTextBox(textBox)
    def setArray(self,array):
        self.arrayLink=array
    def playVis(self,filename,filenameS):
        line=''
        for file in filenameS:
            line+=" "+file
        line=line[1:]
        GaInit.init()
      #  self.arrayLink=["start",filenameS]
        with open("playInf.txt", "w") as f:
            f.write("play:"+line)
        GaInit.start(filename)
        with open("playInf.txt", "w") as f:
            f.write("stop:"+line)
       # self.arrayLink["stop"]
    def runCurrent(self):
        # strem=threading.Thread(target=toMidiMeth.toMidi(),daemon=True)
        s=self.nb.current_tab().getFileDir()
        print(s)
        path=s.split("/")
        s2=""
        for i in range(len(path)-1):
            s2+=path[i]+"/"
        s3=s2
        s2+="midi/"+path[len(path)-1].replace(".txt",".mid")
        s3+="visual/"+path[len(path)-1].replace(".txt","(visual).txt")
        a=toMidiMeth.toMidi(s,0,MIDIFile(1),pohu=True)
        if(not self.BolPlay.get()):
            #print(s)
            #print(self.mypath,s.replace(".txt",".mid"),s.replace(".txt",".mid").replace(self.mypath,self.mypath+"/mid"))
           # print(toMidGa.start(s.replace(".txt",".mid"),toMidGa.start(s.replace(".txt",".mid").replace(self.mypath,self.mypath+"/mid"))))

            strem=threading.Thread(target=toMidGa.start,args=(s2,),daemon=True)
            strem.start()
            #except:
            #    self.entry_text.set( "нет звука! проверьте #")
        else:

            strem=threading.Thread(target=self.playVis,args=(s2,[s3]),daemon=True)
            strem.start()
    def setGraph(self,Graphics):
        self.Graphics=Graphics
    def runAll(self):
        try:
            strem2=threading.Thread(target=createMidi.fullPack, args=(self.mypath,), daemon=True)
            strem2.start()
        except:
            self.entry_text.set( ":(")
    def playNote(self):
        c=0
    def playSame(self):
        c=0
    #entry со временем
    def open_file(self, *args):
        # Open a window to browse to the file you would like to open, returns the directory.
        file_dir = (tkinter
                    .filedialog
                    .askopenfilename(initialdir=self.init_dir, title="Select file", filetypes=self.filetypes))

        # If directory is not the empty string, try to open the file.
        if file_dir:
            try:
                # Open the file.
                file = open(file_dir)

                # Create a new tab and insert at end.
                new_tab = Tab(FileDir=file_dir)
                self.nb.insert( self.nb.index('end')-1, new_tab, text=os.path.basename(file_dir))
                self.nb.select( new_tab )

                # Puts the contents of the file into the text widget.
                self.nb.current_tab().textbox.insert('end', file.read())

                # Update hash
                self.nb.current_tab().status = md5(self.nb.current_tab().textbox.get(1.0, 'end').encode('utf-8'))
            except:
                return
    def open_fileFromDir(self, file_dir):
        # Open a window to browse to the file you would like to open, returns the directory.

        # If directory is not the empty string, try to open the file.
       # print(file_dir)
        if file_dir!=0:
            try:
               # print("kljkljklj")
                # Open the file.
                file = open(file_dir)

                # Create a new tab and insert at end.
                new_tab = Tab(FileDir=file_dir)
                self.nb.insert( self.nb.index('end')-1, new_tab, text=os.path.basename(file_dir))
                self.nb.select( new_tab )

                # Puts the contents of the file into the text widget.
                self.nb.current_tab().textbox.insert('end', file.read())

                # Update hash
                self.nb.current_tab().status = md5(self.nb.current_tab().textbox.get(1.0, 'end').encode('utf-8'))
              #  print("kljkljklj")
            except:
                return
    def save_as(self):
        curr_tab = self.nb.current_tab()

        # Gets file directory and name of file to save.
        file_dir = (tkinter
                    .filedialog
                    .asksaveasfilename(initialdir=self.init_dir, title="Select file", filetypes=self.filetypes, defaultextension='.txt'))

        # Return if directory is still empty (user closes window without specifying file name).
        if not file_dir:
            return False

        # Adds .txt suffix if not already included.
        if file_dir[-4:] != '.txt':
            file_dir += '.txt'

        curr_tab.file_dir = file_dir
        curr_tab.file_name = os.path.basename(file_dir)
        self.nb.tab( curr_tab, text=curr_tab.file_name)

        # Writes text widget's contents to file.
        file = open(file_dir, 'w')
        file.write(curr_tab.textbox.get(1.0, 'end'))
        file.close()

        # Update hash
        curr_tab.status = md5(curr_tab.textbox.get(1.0, 'end').encode('utf-8'))

        return True

    def save_file(self, *args):
        curr_tab = self.nb.current_tab()

        # If file directory is empty or Untitled, use save_as to get save information from user.
        if not curr_tab.file_dir:
            return self.save_as()

        # Otherwise save file to directory, overwriting existing file or creating a new one.
        else:
            with open(curr_tab.file_dir, 'w') as file:
                file.write(curr_tab.textbox.get(1.0, 'end'))

            # Update hash
            curr_tab.status = md5(curr_tab.textbox.get(1.0, 'end').encode('utf-8'))

            return True
    def regularSave(self):
        while True:
            self.saveAll()
            time.sleep(rate*4)
    def saveAll(self):
        for i in range(self.nb.len()-1):
            self.save_fileTab(i)

    def save_fileTab(self, indexTab):
        curr_tab = self.nb.indexed_tab(indexTab)

        # If file directory is empty or Untitled, use save_as to get save information from user.
        if not curr_tab.file_dir:
            return self.save_as()

        # Otherwise save file to directory, overwriting existing file or creating a new one.
        else:
            with open(curr_tab.file_dir, 'w') as file:
                file.write(curr_tab.textbox.get(1.0, 'end'))

            # Update hash
            curr_tab.status = md5(curr_tab.textbox.get(1.0, 'end').encode('utf-8'))

            return True
    def new_file(self, *args):
        # Create new tab
        USER_INP = simpledialog.askstring(title="Name",
                                          prompt="Напишите имя файла")

        new_tab = Tab(FileDir=self.mypath+"/"+USER_INP)
        self.addTabCol(new_tab.getTextBox())
        new_tab.textbox.config(wrap= 'word' if self.word_wrap.get() else 'none')
        self.nb.insert( self.nb.index('end')-1, new_tab, text=new_tab.file_name)
        self.nb.select( new_tab )

    def copy(self):
        # Clears the clipboard, copies selected contents.
        try:
            sel = self.nb.current_tab().textbox.get(tk.SEL_FIRST, tk.SEL_LAST)
            self.master.clipboard_clear()
            self.master.clipboard_append(sel)
        # If no text is selected.
        except tk.TclError:
            pass

    def delete(self):
        # Delete the selected text.
        try:
            self.nb.current_tab().textbox.delete(tk.SEL_FIRST, tk.SEL_LAST)
        # If no text is selected.
        except tk.TclError:
            pass

    def cut(self):
        # Copies selection to the clipboard, then deletes selection.
        try:
            sel = self.nb.current_tab().textbox.get(tk.SEL_FIRST, tk.SEL_LAST)
            self.master.clipboard_clear()
            self.master.clipboard_append(sel)
            self.nb.current_tab().textbox.delete(tk.SEL_FIRST, tk.SEL_LAST)
        # If no text is selected.
        except tk.TclError:
            pass

    def wrap(self):
        if self.word_wrap.get() == True:
            for i in range(self.nb.index('end')-1):
                self.nb.indexed_tab(i).textbox.config(wrap="word")
        else:
            for i in range(self.nb.index('end')-1):
                self.nb.indexed_tab(i).textbox.config(wrap="none")

    def paste(self):
        try:
            self.nb.current_tab().textbox.insert(tk.INSERT, self.master.clipboard_get())
        except tk.TclError:
            pass
    def runSelected(self, event):
        str=self.nb.current_tab().textbox.get(tk.SEL_FIRST, tk.SEL_LAST)
        command=":120;60\n"
        if("chord" in str):
            command+=str+"\n"
            command+="same\n"
            command+="p!\n"
            command+="n0*"+ re.split("\'|\"",str)[1]+"\n"
            command+="end:note\n"
            command+="add('note')\n"
        else:
            command+="same\n"
            if("n" in str):
                command+=str+"\n"
            else:
                command+="n"+str+"\n"
            command+="end:note\n"
            command+="add('note')\n"
        toMidiMeth.toMidi("file",0,MIDIFile(1),line=command,fromStr=True)
        # print(toMidGa.start(s.replace(".txt",".mid"),toMidGa.start(s.replace(".txt",".mid").replace(self.mypath,self.mypath+"/mid"))))

        strem=threading.Thread(target=toMidGa.start,args=("file.mid",),daemon=True)
        strem.start()
    def select_all(self, *args):
        curr_tab = self.nb.current_tab()

        # Selects / highlights all the text.
        curr_tab.textbox.tag_add(tk.SEL, "1.0", tk.END)

        # Set mark position to the end and scroll to the end of selection.
        curr_tab.textbox.mark_set(tk.INSERT, tk.END)
        curr_tab.textbox.see(tk.INSERT)

    def undo(self):
        self.nb.current_tab().textbox.edit_undo()

    def right_click(self, event):
        self.right_click_menu.post(event.x_root, event.y_root)

    def right_click_tab(self, event):
        self.tab_right_click_menu.post(event.x_root, event.y_root)

    def close_tab(self, event=None):
        # Close the current tab if close is selected from file menu, or keyboard shortcut.
        if event is None or event.type == str( 2 ):
            selected_tab = self.nb.current_tab()
        # Otherwise close the tab based on coordinates of center-click.
        else:
            try:
                index = event.widget.index('@%d,%d' % (event.x, event.y))
                selected_tab = self.nb.indexed_tab( index )

                if index == self.nb.index('end')-1:
                    return False

            except tk.TclError:
                return False

        # Prompt to save changes before closing tab
        if self.save_changes(selected_tab):
            # if the tab next to '+' is selected, select the previous tab to prevent
            # automatically switching to '+' tab when current tab is closed
            if self.nb.index('current') > 0 and self.nb.select() == self.nb.tabs()[-2]:
                self.nb.select(self.nb.index('current')-1)

 #############          # self.removeTabCol(selected_tab.getTextBox())

            self.nb.forget( selected_tab )
        else:
            return False

        # Exit if last tab is closed
        if self.nb.index("end") <= 1:
            self.master.destroy()

        return True
    def deliteFileInTab(self,event=None):
        selected_tab = self.nb.current_tab()
        dir=selected_tab.getFileDir()
        self.close_tab(None)
        os.remove(dir)

    def exit(self):
        # Check if any changes have been made.
        for i in range(self.nb.index('end')-1):
            if self.close_tab() is False:
                break

    def save_changes(self, tab):
        # Check if any changes have been made, returns False if user chooses to cancel rather than select to save or not.
        if md5(tab.textbox.get(1.0, 'end').encode('utf-8')).digest() != tab.status.digest():
            # Select the tab being closed is not the current tab, select it.
            if self.nb.current_tab() != tab:
                self.nb.select(tab)

            m = messagebox.askyesnocancel('Editor', 'Do you want to save changes to ' + tab.file_name + '?' )

            # If None, cancel.
            if m is None:
                return False
            # else if True, save.
            elif m is True:
                return self.save_file()
            # else don't save.
            else:
                pass

        return True

    def default_filename(self):
        self.untitled_count += 1
        return 'Untitled' + str(self.untitled_count-1)

    def tab_change(self, event):
        # If last tab was selected, create new tab
        if self.nb.select() == self.nb.tabs()[-1]:
            self.new_file()


def main():
    root = tk.Tk()
    app = Editor(root,"music",style="monokai")
    GraphTestForTab.canvasS(root,winStats="450x450+600+300",path="music",file="chord.txt")
    root.mainloop()
def init(mypath):
    root = tk.Tk()
    app = Editor(root,mypath)
    GraphTestForTab.canvasS(root,winStats="450x450+600+300",path="music",file="chord.txt")
    root.mainloop()
if __name__ == '__main__':
    main()