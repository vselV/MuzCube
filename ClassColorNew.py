from __future__ import annotations

import inspect
from contextlib import suppress
from pathlib import Path
from tkinter import BaseWidget, Event, Menu, Misc, TclError, ttk
from tkinter.font import Font
from typing import Any, Callable, Type, Union
import pygments
import pygments.lexer
import pygments.lexers
#import toml
from pyperclip import copy
from tklinenums import TkLineNumbers
from pygments.styles import get_style_by_name
import tkinter.font as tkFont
import pygments.token as tok
from pygments.token import *
from src.MuzCube.UtilFIles import dataTok
import re


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

color_schemes_dir = Path(__file__).parent / "colorschemes"

LexerType = Union[Type[pygments.lexer.Lexer], pygments.lexer.Lexer]


class Scrollbar(ttk.Scrollbar):
    def __init__(self, master: ColoredBox, autohide: bool, *args, **kwargs) -> None:
        super().__init__(master, *args, **kwargs)
        self.autohide = autohide

    def set(self, low: str, high: str) -> None:
        if self.autohide:
            if float(low) <= 0.0 and float(high) >= 1.0:
                self.grid_remove()
            else:
                self.grid()
        super().set(low, high)


class CodeView(Text):
    _w: str
    _builtin_color_schemes = {"ayu-dark", "ayu-light", "dracula", "mariana", "monokai"}

    def __init__(
            self,
            master: Misc | None = None,
            lexer: LexerType = pygments.lexers.TextLexer,
            color_scheme: dict[str, dict[str, str | int]] | str | None = None,
            tab_width: int = 4,
            linenums_theme: Callable[[], tuple[str, str]] | tuple[str, str] | None = None,
            autohide_scrollbar: bool = True,
            linenums_border: int = 0,
            default_context_menu: bool = False,
            fontName: str = "Courier",
            fontSize: str = "12",
            styleName: str = "monokai",
            **kwargs,
    ) -> None:
        self._frame = ttk.Frame(master)
        self._frame.grid_rowconfigure(0, weight=1)
        self._frame.grid_columnconfigure(1, weight=1)

        kwargs.setdefault("wrap", "none")
        kwargs.setdefault("font", ("monospace", 11))

        linenum_justify = kwargs.pop("justify", "left")

        super().__init__(self._frame, **kwargs)
        super().grid(row=0, column=1, sticky="nswe")

        self._line_numbers = TkLineNumbers(
            self._frame,
            self,
            justify=linenum_justify,
            colors=linenums_theme,
            borderwidth=kwargs.get("borderwidth", linenums_border),
        )
        self._vs = Scrollbar(self._frame, autohide=autohide_scrollbar, orient="vertical", command=self.yview)
        self._hs = Scrollbar(
            self._frame, autohide=autohide_scrollbar, orient="horizontal", command=self.xview
        )

        self._line_numbers.grid(row=0, column=0, sticky="ns")
        self._vs.grid(row=0, column=2, sticky="ns")
        self._hs.grid(row=1, column=1, sticky="we")

        super().configure(
            yscrollcommand=self.vertical_scroll,
            xscrollcommand=self.horizontal_scroll,
            tabs=Font(font=kwargs["font"]).measure(" " * tab_width),
        )

        self._context_menu = None
        self._default_context_menu = default_context_menu
        if default_context_menu:
            self.context_menu

        contmand = "Command" if self._windowingsystem == "aqua" else "Control"

        super().bind(f"<{contmand}-c>", self._copy, add=True)
        super().bind(f"<{contmand}-v>", self._paste, add=True)
        super().bind(f"<{contmand}-a>", self._select_all, add=True)
        super().bind(f"<{contmand}-Shift-Z>", self.redo, add=True)
        super().bind("<<ContentChanged>>", self.scroll_line_update, add=True)
        super().bind("<Button-1>", self._line_numbers.redraw, add=True)

        self._orig = f"{self._w}_widget"
        self.tk.call("rename", self._w, self._orig)
        self.tk.createcommand(self._w, self._cmd_proxy)

        self._set_lexer(lexer)
        self._set_color_scheme(color_scheme)

        self._line_numbers.redraw()

        self.lines_start_states=[]

        self.boxes=[]
        self.binds=[]
        self.fontName=fontName
        self.fontSize=fontSize
        self.styleName=styleName
        self.token_to_tag={}
        self.masTags=[]
        self.colors={}
        self.lexer=lexer

        self.simpleLexer=False
        self.MuseCube=True
    @property
    def context_menu(self) -> Menu:
        if self._context_menu is None:
            self._context_menu = self._create_context_menu()

        return self._context_menu

    def _create_context_menu(self) -> Menu:
        context_menu = Menu(self, tearoff=0)
        popup_callback = lambda e: context_menu.tk_popup(e.x_root + 5, e.y_root + 5)

        if self._windowingsystem == "aqua":
            super().bind("<Button-2>", popup_callback)
            super().bind("<Control-Button-1>", popup_callback)
        else:
            super().bind("<Button-3>", popup_callback)

        if self._default_context_menu:
            contmand = "⌘" if self._windowingsystem == "aqua" else "Ctrl"

            context_menu.add_command(
                label="Undo", accelerator=f"{contmand}+Z", command=lambda: self.event_generate("<<Undo>>")
            )
            context_menu.add_command(
                label="Redo", accelerator=f"{contmand}+Y", command=lambda: self.event_generate("<<Redo>>")
            )
            context_menu.add_separator()
            context_menu.add_command(
                label="Cut", accelerator=f"{contmand}+X", command=lambda: self.event_generate("<<Cut>>")
            )
            context_menu.add_command(label="Copy", accelerator=f"{contmand}+C", command=self._copy)
            context_menu.add_command(label="Paste", accelerator=f"{contmand}+V", command=self._paste)
            context_menu.add_command(
                label="Select all", accelerator=f"{contmand}+A", command=self._select_all
            )

        return context_menu

    def _select_all(self, *_) -> str:
        self.tag_add("sel", "1.0", "end")
        self.mark_set("insert", "end")
        return "break"

    def redo(self, event: Event | None = None) -> None:
        try:
            self.edit_redo()
        except TclError:
            pass

    def _paste(self, *_):
        insert = self.index(f"@0,0 + {self.cget('height') // 2} lines")

        with suppress(TclError):
            self.delete("sel.first", "sel.last")
            self.tag_remove("sel", "1.0", "end")
            self.insert("insert", self.clipboard_get())

        self.see(insert)

        return "break"

    def _copy(self, *_):
        text = self.get("sel.first", "sel.last")
        if not text:
            text = self.get("insert linestart", "insert lineend")

        copy(text)

        return "break"

    def _cmd_proxy(self, command: str, *args) -> Any:
        try:
            if command in {"insert", "delete", "replace"}:
                start_line = int(str(self.tk.call(self._orig, "index", args[0])).split(".")[0])
                end_line = start_line
                if len(args) == 3:
                    end_line = int(str(self.tk.call(self._orig, "index", args[1])).split(".")[0]) - 1
            result = self.tk.call(self._orig, command, *args)
        except TclError as e:
            error = str(e)
            if 'tagged with "sel"' in error or "nothing to" in error:
                return ""
            raise e from None

        if command == "insert":
            if not args[0] == "insert":
                start_line -= 1
            lines = args[1].count("\n")
            if lines == 1:
                self.highlight_line(f"{start_line}.0")
            else:
                self.highlight_area(start_line, start_line + lines)
            self.event_generate("<<ContentChanged>>")
        elif command in {"replace", "delete"}:
            if start_line == end_line:
                self.highlight_line(f"{start_line}.0")
            else:
                self.highlight_area(start_line, end_line)
            self.event_generate("<<ContentChanged>>")

        return result

    def _setup_tags(self, tags: dict[str, str]) -> None:
        for key, value in tags.items():
            if isinstance(value, str):
                self.tag_configure(f"Token.{key}", foreground=value)
    def createTag(self,name,params,fontName,fontSize,**kwargs):
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
                    self.tag_config(name,foreground=split[i])
                    self.colors[name]=split[i]
                else:
                    if ":" in split[i]:
                        sc=split[i].split(":")
                        if sc[0] == "bg":
                            if(sc[1]!=""):
                                self.tag_config(name,background=sc[1])
                            else:
                                self.tag_config(name,background=style.background_color)
                        elif sc[0] == "border":
                            if(sc[1]!=""):
                                self.tag_config(name,border=sc[1])
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
                            self.tag_config(name,underline=True)
                        elif split[i]=="nounderline":
                            self.tag_config(name,underline=False)
        if(bold and italic):
            self.tag_config(name,font=tkFont.Font(family=fontName,size=int(fontSize),weight=tkFont.BOLD, slant=tkFont.ITALIC))
        elif(bold):
            self.tag_config(name,font=(fontName,fontSize,"bold"))
        elif(italic):
            self.tag_config(name,font=(fontName,fontSize,"italic"))
    def configureTextBox(self,masTags,fontName,fontSize,styleName,token_to_tag):
        style=get_style_by_name(styleName)
        self.config(font=(fontName,fontSize),background=style.background_color,selectbackground=style.highlight_color)
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
                        self.createTag(getType(token), dictBase[dataTok.STANDARD_TYPES_SP[token][ct2]], fontName, fontSize, style=style)
                    else:
                        if(dictBase.get(dataTok.STANDARD_TYPES_SP[token][ct3], None) is not None):
                            self.createTag(getType(token),
                                           dictBase[dataTok.STANDARD_TYPES_SP[token][ct2]], fontName, fontSize, style=style,
                                           parrentBool=dictIntBools[dataTok.STANDARD_TYPES_SP[token][ct3]])
                        ct3+=1
                    ct2+=1
                ct+=1
       # for
        self.config(insertbackground=self.getColor(Name))
    def _setup_tags_none(self):
        self.configureTextBox(self.masTags,self.fontName,self.fontSize,self.styleName,self.token_to_tag)
    def highlight_line(self, index: str) -> None:
        line_num = int(self.index(index).split(".")[0])
        for tag in self.tag_names(index=None):
            if tag.startswith("Token"):
                self.tag_remove(tag, f"{line_num}.0", f"{line_num}.end")

        line_text = self.get(f"{line_num}.0", f"{line_num}.end")
        start_col = 0

        for token, text in pygments.lex(line_text, self._lexer):
            token = str(token)
            end_col = start_col + len(text)
            if token not in {"Token.Text.Whitespace", "Token.Text"}:
                self.tag_add(token, f"{line_num}.{start_col}", f"{line_num}.{end_col}")
            start_col = end_col

    def highlight_all(self) -> None:
        for tag in self.tag_names(index=None):
            if tag.startswith("Token"):
                self.tag_remove(tag, "1.0", "end")

        lines = self.get("1.0", "end")
        line_offset = lines.count("\n") - lines.lstrip().count("\n")
        start_index = str(self.tk.call(self._orig, "index", f"1.0 + {line_offset} lines"))

        for token, text in pygments.lex(lines, self._lexer):
            token = str(token)
            end_index = self.index(f"{start_index} + {len(text)} chars")
            if token not in {"Token.Text.Whitespace", "Token.Text"}:
                self.tag_add(token, start_index, end_index)
            start_index = end_index

    def highlight_area(self, start_line: int | None = None, end_line: int | None = None) -> None:
        for tag in self.tag_names(index=None):
            #if tag.startswith("Token"):
            self.tag_remove(tag, f"{start_line}.0", f"{end_line}.end")

        text = self.get(f"{start_line}.0", f"{end_line}.end")
        line_offset = text.count("\n") - text.lstrip().count("\n")
        start_index = str(self.tk.call(self._orig, "index", f"{start_line}.0 + {line_offset} lines"))

        if(self.simpleLexer):
            lexed= self._lexer.get_tokens_unprocessed(text)
        else:
            context= LexerContext(text,0,stack=self.lines_start_states)
            lexed= self._lexer.get_tokens_unprocessed(text=text,context=context)
        for i, token_type, text in lexed:
            token = str(token_type)
            end_index = self.index(f"{start_index} + {len(text)} indices")
            if token not in {"Token.Text.Whitespace", "Token.Text"}:
               # self.tag_add(token, start_index, end_index)
                if token_type in self.base.token_to_tag:
                    self.textBox.tag_add(self.token_to_tag[token_type], start_index, end_index)
                else:
                    mas= dataTok.STANDARD_TYPES_SP[token_type]
                    for k in range(len(mas)-1):
                        if dataTok.STANDARD_TYPES_SP[token_type][ln - c] in self.base.masTags:
                            self.textBox.tag_add(dataTok.STANDARD_TYPES_SP[token_type][ln - c], si, sj)
                            break
                        c+=1
                    if(c==ln):
                        self.textBox.tag_add("tok", si, sj)
            start_index = end_index
     #   for token, text in lexed:
       #     token = str(token)
        #    end_index = self.index(f"{start_index} + {len(text)} indices")
        #    if token not in {"Token.Text.Whitespace", "Token.Text"}:
        #        self.tag_add(token, start_index, end_index)
         #   start_index = end_index
'''
    def _set_color_scheme(self, color_scheme: dict[str, dict[str, str | int]] | str | None) -> None:
        if isinstance(color_scheme, str) and color_scheme in self._builtin_color_schemes:
            color_scheme = toml.load(color_schemes_dir / f"{color_scheme}.toml")
        elif color_scheme is None:
            color_scheme = toml.load(color_schemes_dir / "dracula.toml")

        assert isinstance(color_scheme, dict), "Must be a dictionary or a built-in color scheme"

        config, tags = _parse_scheme(color_scheme)
        self.configure(**config)
        self._setup_tags(tags)

        self.highlight_all()
'''
    def _set_lexer(self, lexer: LexerType) -> None:
        self._lexer = lexer() if inspect.isclass(lexer) else lexer
        self.highlight_all()

    def __setitem__(self, key: str, value) -> None:
        self.configure(**{key: value})

    def __getitem__(self, key: str) -> Any:
        return self.cget(key)

    def configure(self, **kwargs) -> None:
        lexer = kwargs.pop("lexer", None)
        color_scheme = kwargs.pop("color_scheme", None)

        if lexer is not None:
            self._set_lexer(lexer)

        if color_scheme is not None:
            self._set_color_scheme(color_scheme)

        super().configure(**kwargs)

    config = configure

    def pack(self, *args, **kwargs) -> None:
        self._frame.pack(*args, **kwargs)

    def grid(self, *args, **kwargs) -> None:
        self._frame.grid(*args, **kwargs)

    def place(self, *args, **kwargs) -> None:
        self._frame.place(*args, **kwargs)

    def pack_forget(self) -> None:
        self._frame.pack_forget()

    def grid_forget(self) -> None:
        self._frame.grid_forget()

    def place_forget(self) -> None:
        self._frame.place_forget()

    def destroy(self) -> None:
        for widget in self._frame.winfo_children():
            BaseWidget.destroy(widget)
        BaseWidget.destroy(self._frame)

    def horizontal_scroll(self, first: str | float, last: str | float) -> CodeView:
        self._hs.set(first, last)

    def vertical_scroll(self, first: str | float, last: str | float) -> CodeView:
        self._vs.set(first, last)
        self._line_numbers.redraw()

    def scroll_line_update(self, event: Event | None = None) -> CodeView:
        self.horizontal_scroll(*self.xview())
        self.vertical_scroll(*self.yview())
