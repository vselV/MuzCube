from pygments.token import *
from pygments.lexer import ExtendedRegexLexer
from pygments.lexers.python import PythonLexer
from pygments.lexer import DelegatingLexer, RegexLexer, include, \
    bygroups, using, default, words, combined, this,inherit
class modifiPython(PythonLexer):
    tokens = {
        'builtins': [
            (words((
                "root","oct","inst","vel","edo","valOct","chan","reLen","setScale",
                "add","SM",
                "load","swap",
                "chord","pattern","scale","arpeg",
                "fix","turn","tp","getState","setState","unBind","noteBind",
                "addNote"), prefix=r'(?<!\.)', suffix=r'\b'),
             Name.Builtin),
            inherit,
        ]
    }
class witchVar(modifiPython):
    tokens = {
        'magicvars': [
            (words((
                "rootm","currentLen","octave",
                "instr","veloc","EDO","EDOconst",
                "GlobalChanel","timePoint"), prefix=r'(?<!\.)', suffix=r'\b'),
             Name.Variable.Magic),
            inherit,
        ]
    }
class MuzCubeLexer(ExtendedRegexLexer):
    name = 'MuzCube'
    aliases = ['muzcube']
    filenames = ['*.muz']
    
    in_out=0
    regex_return=r"\n"
    
    CreateStates=["arp_state","pat_state","ch_scale"]
    CreateOutStates=["arp_notes","pat","notes_only"]
    
    noSCOB = ["fix","turn","getState","setState","unBind"]
    withArg = ["vel","root","chan","reLen","setScale","edo","oct","valOct","setBase"]
    withArgNotStr = ["chan","tp","edo","oct","valOct","setBase"]

    allCommands=[["root","oct","inst","vel","edo","valOct","chan","reLen","setScale"],["add","SM"],["same"],["end"]]
    def first_calback(lexer, match,ctx):
        if match.start() == 0:
            if "#" in match.group():
                yield match.start(), Comment, match.group()
            else:
                yield match.start(), Number, match.group()
        else:
            yield match.start(), Error, match.group()
        ctx.pos=match.end()
    def calback_in_out(lexer, match,ctx):
        yield match.start(), Operator, match.group()
        ctx.pos=match.end()
        lexer.in_out=1
    def calback_close(lexer, match, ctx):
        if lexer.in_out==1:
            while ctx.stack[-1] != 'root':
                ctx.stack.pop()
            lexer.in_out=0
        else:
            while ctx.stack[-1] != 'inSame':
                ctx.stack.pop()
        yield match.start(), Whitespace, match.group()
        ctx.pos=match.end()
    def calback_to_n(lexer,match,ctx):
        while ctx.stack[-1] != 'notes':
            ctx.stack.pop()
        yield match.start(), Whitespace, match.group()
        ctx.pos=match.end()
    def isNum(self,str):
        try:
            int(str)
            float(str)
            return 1
        except:
            return 0
    def isStr(self,str):
        if(str[-1]==str[0]=='"'):
            for i in str:
                if i == '"':
                    return 0
            return 1
        if(str[-1]==str[0]=="'"):
            for i in str:
                if i == "'":
                    return 0
            return 1
        return 0
    def one_calback(lexer,match,ctx):
        if lexer.isNum(match.group()) == 1:
            yield match.start(), Number, match.group()
        elif lexer.isStr(match.group())==1:
            yield match.start(), String, match.group()
        else:
            yield match.start(), Error, match.group()
        ctx.pos=match.end()
    def numStrCall(lexer,match,ctx):
        if lexer.isNum(match.group()) == 1:
            yield match.start(), Number, match.group()
        else:
            yield match.start(), String, match.group()
        ctx.pos=match.end()
    def difine_calback(lexer,match,ctx):
        l=len(ctx.stack)-1
        while(not ctx.stack[l] in lexer.CreateStates):
            l-=1
        name=lexer.CreateStates.index(ctx.stack[l])
        name=lexer.CreateOutStates[name]
        print(name)
        if(match.group()=="'"):
            lexer.patternChar="'"
            ctx.stack.append(name+"2")
        else:
            lexer.patternChar='"'
            ctx.stack.append(name+"1")
        print(ctx.stack[-1])
        yield match.start(), String, match.group()
        ctx.pos=match.end()
    patternChar=""
    isCal=0
    def pattern_calback(lexer,match,ctx):
        if("pattern" in match.group()):
            yield match.start(1), Name.Class, match.group(1)
            yield match.start(2), Whitespace, match.group(2)
            yield match.start(3), Name, match.group(3)
            lexer.isCal=1
        elif(match.group() =="'" or match.group() == '"'):
            yield match.start(), String, match.group()
            lexer.patternChar=match.group()
        else:
            yield match.start(), Error, match.group()
        ctx.pos=match.end()
    def cm_calback(lexer,match,ctx):
        yield match.start(1), Name.Constant, match.group(1)
        yield match.start(2), Whitespace, match.group(2)
        yield match.start(3), Name, match.group(3)
        yield match.start(4), Whitespace, match.group(4)
        yield match.start(5), String, match.group(5)
        if(match.group(5)=="'"):
            ctx.stack.append("pat2")
        else:
            ctx.stack.append("pat1")
        lexer.patternChar=match.group(5)
        lexer.isCal=2
        ctx.pos=match.end()
    def pattern_return(lexer,match,ctx):
        if(match.group()==lexer.patternChar):
            if(lexer.isCal==1):
                while ctx.stack[-1] != 'pat_state':
                    ctx.stack.pop()
                lexer.patternChar=""
                yield match.start(), String, match.group()
            elif(lexer.isCal==2):
                while ctx.stack[-1] != 'simp_args':
                    ctx.stack.pop()
                lexer.patternChar=""
                lexer.isCal=0
                yield match.start(), String, match.group()
            else:
                yield match.start(), Error, match.group()
        else:
            yield match.start(), Error, match.group()
        ctx.pos=match.end()
    def fin_ret(lexer,match,ctx):
        lexer.isCal=0
        yield match.start(), Name, match.group()
        ctx.pos=match.end()
    tokens = {
        'root': [
            (r'^(#?:[\d#]+;[\d#]+ *#*)',first_calback),
            (r'\s', Whitespace),
            (r';', Name),
            (r'((?<=\n)#|^#).*?$', Comment),
            (r'same', Keyword, ('end','inSame')),
            (r'(add)([ \t]*)(\()', bygroups(Name.Constant,Whitespace,Name),'simp_args'),
            (r'add', Name.Constant,'add'),
            include('setWords'),
            include('swapWords'),
            include('fixWords'),
            include('createWords'),
            include('numbers'),
            include('punctuation'),
            include('pyWords_in'),
            (r'\w+', Name),
        ],
        'SM' :[
            (r'[ \t]', Whitespace),
            (r':', Operator,'end_add'),
            (r';', Name, '#pop'),
            (r"\n",Whitespace, '#pop'),
        ],
        'add' :[
            (r'[ \t]', Whitespace),
            (r';', Name, '#pop'),
            (r"\n",Whitespace, '#pop'),
            (r'>', calback_in_out, 'outSame'),
            (r':', Operator,'end_add'),
        ],
        'end_add': [
            (r':', Operator),
            (r'(?<=:)[\w\.]+?$', String),
            (r'[\n;]', String,('#pop','#pop'))
        ],
        'inSame': [
            (r'\n', Whitespace),
            (r'end', Keyword, '#pop'),
            include('same')
        ],
        'outSame': [
            (r'\n',calback_close),
            include('same')
        ],
        'same': [
            (r'\t ', Whitespace),
            (r';', Name),
            (r'((?<=\n)#|^#).*?$', Comment),
            (r'((^p)|((?<=[ \t;\n>])p))', Operator, 'modyfer'),
            (r'((^n)|((?<=[ \t;\n>])n))', Operator, 'notes'),
            (r'(SM)([ \t]*)(\()', bygroups(Name.Constant,Whitespace,Name),'simp_args'),
            (r'SM', Name.Constant,'SM'),
            include('setWords'),
            include('swapWords'),
            include('fixWords'),
            include('createWords'),
            include('numbers'),
            include('punctuation'),
            (r'\w+', Name),
        ],
        'modyfer': [
            (r'(!!|!|@|#|\$|%|\^|&)\.?\.?t?\.?\.?\d*\.?\.?', Number),
            (r';',  Name, '#pop'),
            (r'\n',calback_close)
        ],
        'notes': [
            include('notes_only'),
            include('note_operators'),
            (r'\*', Operator,'chord'),
            (r';', Name, '#pop'),
            (r"\n",calback_close),
        ],
        'note_operators':[
            (r'(\+|-|v|:|=|`)', Operator),
            (r'(?<=(`))(\[((\d+(\.\d*)?),)*(\d+(\.\d*)?)+\])', Number),
            (r'(?<=(:|=))(!!|!|@|#|\$|%|\^|&)\.?\.?t?\.?\.?\d*\.?\.?', Number),
            (r'(?<=(\+|-|v))\d+', Number),
        ],
        'notes_only':[
            (r'\.', Name),
            (r'(?<=(n| |\t))_', Number),
            (r'(?<=(n| |\t))(\+|-)?\d+(t|f|e|c)', Number),
            (r'(?<=(n| |\t))((\+|-)?\d+?(x|\/|\^)?)+?f', Number),
            (r'(?<=(n| |\t))((\+|-)?\d+\.)*\d+', Number),
            (r' ', Token.Text.Whitespace),
        ],
        'notes_only1':[
            (r'\.', Name),
            (r'(?<=("| |\t))(\+|-)?\d+(t|f|e|c)', Number),
            (r'(?<=("| |\t))((\+|-)?\d+?(x|\/|\^)?)+?f', Number),
            (r'(?<=("| |\t))((\+|-)?\d+\.)*\d+', Number),
            (r'"', String,('#pop','#pop','#pop')),
            (r' ', Token.Text.Whitespace)
        ],
        'notes_only2':[
            (r'\.', Name),
            (r"(?<=('| |\t))(\+|-)?\d+(t|f|e|c)", Number),
            (r"(?<=('| |\t))((\+|-)?\d+?(x|\/|\^)?)+?f", Number),
            (r"(?<=('| |\t))((\+|-)?\d+\.)*\d+", Number),
            (r"'", String,('#pop','#pop','#pop')),
            (r' ', Token.Text.Whitespace)
        ],
        'chord': [
            (r'[\w\.]+', String),
            (r'\$\$',Operator,'arpeg'),
            (r' ', calback_to_n),
            (r';', Token.Text.Whitespace, ('#pop','#pop')),
            (r"(?<=(,))(\+|-)?\d+(t|f|e|c)", Number),
            (r"(?<=(,))((\+|-)?\d+?(x|\/|\^)?)+?f", Number),
            (r"(?<=(,))((\+|-)?\d+\.)*\d+", Number),
            (r'\n',calback_close),
            include('punctuation')
        ],
        'arpeg': [
            (r'[\w\.]+', String),
            (r'>',Operator,'cf'),
            (r' ', calback_to_n),
            (r';', Token.Text.Whitespace, ('#pop','#pop','#pop')),
            (r'\n',calback_close)
        ],
        'cf': [
            (r'(\d+)(\.\d*)?', Number),
            (r' ', calback_to_n),
            (r';', Token.Text.Whitespace, ('#pop','#pop','#pop','#pop')),
            (r'\n',calback_close)
        ],
        'return':[
            (r'[\n;]', Whitespace,"#pop"),
        ],
        'end': [
            (r':', Operator),
            (r'(?<=:)[\w\.]+?$', String),
            (r';', Name,'#pop'),
            (r'\n', Whitespace,'#pop')
        ],
        'str': [
            (r'[^*/]+', Comment.Multiline),
            (r'/\*', Comment.Multiline, '#push'),
            (r'\*/', Comment.Multiline, '#pop'),
            (r'[*/]', Comment.Multiline)
        ],
        'numbers': [
            (r'(\d+\.\d*|\d*\.\d+)([eE][+-]?[0-9]+)?j?', Number.Float),
            (r'\d+[eE][+-]?[0-9]+j?', Number.Float),
            (r'0[0-7]+j?', Number.Oct),
            (r'0[bB][01]+', Number.Bin),
            (r'0[xX][a-fA-F0-9]+', Number.Hex),
            (r'\d+L', Number.Integer.Long),
            (r'\d+j?', Number.Integer)
        ],
        'punctuation': [
            (r'[\(\)\[\]]', Name),
            (r',', Punctuation)
        ],
        'comment': [
            (r'[^*/]+', Comment.Multiline),
            (r'/\*', Comment.Multiline, '#push'),
            (r'\*/', Comment.Multiline, '#pop'),
            (r'[*/]', Comment.Multiline)
        ],
        'set_words_after:':[
            (r'(?<=:).+?(?=[\n;|\'\"])', numStrCall,'#pop'),
            (r'"', pattern_return),
            (r"'", pattern_return),
            (r';', Name,('#pop','#pop')),
            (r'\|', Name,('#pop','#pop')),
            (r'\n', Whitespace,('#pop','#pop')),
        ],
        'set_words_after(':[
            include('numbers'),
            include('simp_string'),
            (r'(?<=(\()).+?(?=[\)])', numStrCall),
            (r',', Name),
            (r'\)',  Name,'#pop'),
            (r'[\t ]', Whitespace),
            (r';', Name,('#pop','#pop')),
            (r'\|', Name,('#pop','#pop')),
            (r'"', pattern_return),
            (r"'", pattern_return),
            (r'\n', Whitespace,('#pop','#pop')),
        ],
        'setWords': [
            (words((
                "root","oct","inst","vel","edo","valOct","chan","reLen","setScale","load","setBase"), suffix=r'\b'),
             Name.Function,"setChoice"),
        ],
        'setChoice': [
            (r'[\t ]', Whitespace),
            (r':', Operator,'set_words_after:'),
            (r'\(', Name,'set_words_after('),
            (r';', Name,'#pop'),
            (r'\|', Name,'#pop'),
            (r'"', pattern_return),
            (r"'", pattern_return),
            (r'\n', Whitespace,'#pop'),
        ],
        'createWords': [
            (r'(arpeg)( *)(\()', bygroups(Name.Class,Whitespace,Name), 'arp_state'),
            (r'(pattern)( *)(\()', pattern_calback, 'pat_state'),
            (r'(chord)( *)(\()', bygroups(Name.Class,Whitespace,Name), 'ch_scale'),
            (r'(scale)( *)(\()', bygroups(Name.Class,Whitespace,Name), 'ch_scale'),
        ],
        'pat1' :[
            include('setWords'),
            (r"[ \t]", String),
            (r'\|', Name),
            (r'"', pattern_return),
            (r'[\w\.]+',  String),
        ],
        'pat2' :[
            include('setWords'),
            (r"[ \t]", String),
            (r'\|', Name),
            (r"'", pattern_return),
            (r'[\w\.]+', String),
        ],
        'pat_state' :[
            include('args2'),
            (r'"', String,'in_string1'),
            (r"'", String,'in_string2'),
        ],
        'arp_notes1' :[
            (r'\.', Name),
            (r'(?<=(\(|,|"| |\t))(\+|-)?\d+(t|f|e|c)', Number),
            (r'(?<=(\(|,|"| |\t))((\+|-)?\d+?(x|\/|\^)?)+?f', Number),
            (r'(?<=(\(|,|"| |\t))((\+|-)?\d+\.)*\d+', Number),
            (r'"', String,('#pop','#pop','#pop')),
            include('note_operators'),
            include('punctuation'),
            (r' ', Token.Text.Whitespace)
        ],
        'arp_notes2' :[
            (r'\.', Name),
            (r"(?<=(\(|,|'| |\t))(\+|-)?\d+(t|f|e|c)", Number),
            (r"(?<=(\(|,|'| |\t))((\+|-)?\d+?(x|\/|\^)?)+?f", Number),
            (r"(?<=(\(|,|'| |\t))((\+|-)?\d+\.)*\d+", Number),
            (r"'", String,('#pop','#pop','#pop')),
            include('note_operators'),
            include('punctuation'),
            (r' ', Token.Text.Whitespace)
        ],
        'ch_scale' :[
            include('args2'),
            (r'"', String,'in_string1'),
            (r"'", String,'in_string2'),
        ],
        'arp_state' : [
            include('args2'),
            (r'"', String,'in_string1'),
            (r"'", String,'in_string2'),
        ],
        'in_string1' : [
            (r'[\w\.]+', String),
            (r'"', String,'next_arg')
        ],
        'in_string2' : [
            (r'[\w\.]+', String),
            (r"'", String,'next_arg')
        ],
        'simp_string1' : [
            (r'[^"]+', String),
            (r'"', String,'#pop'),
            (r";", Name,'#pop'),
            (r"\n", Whitespace,'#pop')
        ],
        'simp_string2' : [
            (r"[^']+", String),
            (r"'", String,'#pop'),
            (r";", Name,'#pop'),
            (r"\n", Whitespace,'#pop')
        ],
        'simp_string' : [
            (r'"', String,'simp_string1'),
            (r"'", String,'simp_string2')
        ],
        'next_arg' : [
            (r",",Punctuation),
            (r' ', Whitespace),
            (r'"', difine_calback), #calbacs и ниже в стек и решать
            (r"'", difine_calback),
        ],
        'kwarg' : [
            (r' ', Whitespace),
            (r'\w+', Name.Constant),
            (r'=', Name,'kwarg_after'),
            (r'\)',Name,'#pop'),
        ],
        'kwarg_after' : [
            (r' ', Whitespace),
            (r'[\"\'\w\.\+-]+', one_calback,('#pop','#pop')),
            (r'\)', Name,('#pop','#pop')),
        ],
        'args2' :[
            (r'[ \t]', Whitespace),
            (r',', Punctuation,"kwarg"),
            (r"\)", fin_ret,'#pop'),
        ],
        'oneWords': [
            (words((
                "chord","pattern","scale","arpeg"), suffix=r'\b'),
             Name.Class),
        ],
        'simp_args':[
            (r"(cm)([ \t]*)(=)([ \t]*)('|\")",
             cm_calback),
            (r'(cm)([ \t]*)(=)([ \t]*)(")', Name),
            include('numbers'),
            include('simp_string'),
            (r",", Name),
            (r"\)", Name,'#pop'),
            (r';', Name,'#pop'),
            (r'\n', Whitespace,'#pop'),
            (r'[A-Za-z]',Name.Constant),
            (r'=',Name)
        ],
        'fixWords': [
            (words((
                "fix","turn","tp","getState","setState","unBind","noteBind"), suffix=r'\b'),
             Name.Decorator,"setChoice"),
        ],
        'scriptContent2': [
            (r"((.|\n|\r)+)(endPy)", bygroups(using(modifiPython), Keyword),("#pop","#pop")),
            (r"((.|\n|\r)+$)",using(witchVar))
        ],
        'scriptContent1': [
            (r":",Operator),
            (r"(?<=:)1",Number,'scriptContent2'),
            (r"((.|\n|\r)+)(endPy)", bygroups(using(modifiPython), Keyword),"#pop"),
            (r"((.|\n|\r)+$)", using(modifiPython))
        ],
        'pyWords_in': [
            (words((
                "pyGlobal","pyLocal"), suffix=r'\b'),
             Keyword,'scriptContent1'),
        ],
        'preSimp': [
            ( r"([ \t] *)(\()",bygroups(Name, Whitespace),("#pop","simp_args")),
            ],
        'swapWords': [
            (words((
                "load","swap"), suffix=r'\b'),
             Name.Decorator, 'preSimp'),
        ]
    }
