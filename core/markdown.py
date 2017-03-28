import ply.lex as lex
import ply.yacc as yacc

#dont forget to add 1x\n
text = '''# Sli is a perl wizard
## hello
### yy
#### pppp
test
this is a test


Sli is a ~bad programmer~ **bery good programmer** *yes*
Sli **sucks**


__underlined text__
Hello ima *faggot* ^exposant^ _underline_

`hello ima code`

`hello ime *troll* code`'''

if text[-1] != '\n':
    text = text + "\n"

print(text)

tokens = (
    'ESCAPE', 
    'CODE', #done
    'EMPTY_LINE', #done
    'EOL', #done
    'HEADER', #done 
    'UNORDERED_LIST',
    'ORDERED_LIST',
    'SEMPHASIS', #done
    'LEMPHASIS', #done
    'STRIKETHROUGH',#done
    'UNDERLINE', #done
    'EXPOSANT', #done
    'INDICE', #done
    'LPARENTHESIS', 
    'RPARENTHESIS',
    'LBRACKET',
    'RBRACKET',
    'BLOCKQUOTES', 
    'SPACE', #done
    'WORD', #done
)


#Rules
t_ESCAPE          = r'\\'
t_CODE            = r'`.*?`'
t_EMPTY_LINE      = r'(?m)^\n'
t_EOL             = r'\n'
t_HEADER          = r'(?m)^\#+'
t_UNORDERED_LIST  = r'(?m)^\*'
t_ORDERED_LIST    = r'(?m)^[0-9]+'
t_SEMPHASIS       = r'\*{2}.*?\*{2}'
t_LEMPHASIS       = r'\*.*?\*'
t_STRIKETHROUGH   = r'~.*?~'
t_UNDERLINE       = r'\_{2}.*?\_{2}'
t_EXPOSANT        = r'\^.*?\^'
t_INDICE          = r'\_.*?\_'
t_LPARENTHESIS    = r'\('
t_RPARENTHESIS    = r'\)'
t_LBRACKET        = r'\['
t_RBRACKET        = r'\]'
t_BLOCKQUOTES     = r'(?m)^>'
t_SPACE           = r'\ '
t_WORD            = r'\b\S+\b'


def t_error(t):
    print("Illegal character '%s'" % t.value[0])
    t.lexer.skip(1)


lexer = lex.lex()
lexer.input(text)


while True:
    tok = lexer.token()
    if not tok:
        break
    print(tok)



# --- Parser ---
def p_text_complex(p):
    '''text : text text'''
    p[0] = p[1] + p[2]


def p_text(p):
    '''text : line
            | EMPTY_LINE
            | header_line'''
    p[0] = p[1]


def p_line_general(p):
    '''line : sentence EOL'''
    p[0] = p[1] + ' '


def p_header_line(p):
    '''header_line : HEADER sentence EOL'''

    if p[2][0] == " ": #remove unecessary first space on title
        p[2] = p[2][1:]

    p[0] = "<h" + str(len(p[1]))  + ">" + p[2] + "</h" + str(len(p[1]))  + ">" + p[3]


def p_sentence_complex(p):
    '''sentence : sentence sentence'''
    p[0] = p[1] + p[2]


def p_sentence_stong_emphasis(p):
    '''sentence : SEMPHASIS'''
    p[0] = "<b>" + p[1][2:-2] + "</b>"

def p_sentence_light_emphasis(p):
    '''sentence : LEMPHASIS'''
    p[0] = "<i>" + p[1][1:-1] + "</i>"

def p_sentence_strikethrough(p):
    '''sentence : STRIKETHROUGH'''
    p[0] = "<strike>" + p[1][1:-1] + "</strike>"

def p_sentence_underline(p):
    '''sentence : UNDERLINE'''
    p[0] = "<span class=\"underline\">" + p[1][2:-2]  + "</span>"

def p_sentence_exposant(p):
    '''sentence : EXPOSANT'''
    p[0] = "<sup>" + p[1][1:-1] + "</sup>"

def p_sentence_indice(p):
    '''sentence : INDICE'''
    p[0] = "<sub>" + p[1][1:-1] + "</sup>"

def p_sentence_inline_code(p):
    '''sentence : CODE'''
    p[0] = "<code>" + p[1][1:-1] + "</code>"


def p_sentence_word(p):
    '''sentence : WORD
                | SPACE'''
    p[0] = p[1]



def p_error(p):
    print("error %s" % p)
   

parser = yacc.yacc()

output = parser.parse(text)
print(output)
