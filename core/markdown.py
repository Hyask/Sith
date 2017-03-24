import ply.lex as lex
import ply.yacc as yacc

#dont forget to add 1x\n
text = '''Sli is bad
wut

Sli sucksx2
Sli sucks


Hello emphasis ima faggot exposant
'''

print(text)

tokens = (
    'ESCAPE',
    'EMPTY_LINE',
    'EOL',
    'HEADER',
    'ORDERED_LIST',
    'DOUBLE_STAR',
    'STAR',
    'STRIKETHROUGH',
    'UNDERLINE', #MarkdownAE addition
    'EXPOSANT', #MarkdownAE addition
    'INDICE', #MarkdownAE addition
    'LPARENTHESIS',
    'RPARENTHESIS',
    'LBRACKET',
    'RBRACKET',
    'BLOCKQUOTES',
    'CODE',
    'SPACE',
    'WORD',
)


#Rules
t_ESCAPE          = r'\\'
t_EMPTY_LINE      = r'(?m)^\n'
t_EOL             = r'\n'
t_HEADER          = r'(?m)^\#'
t_ORDERED_LIST    = r'(?m)^[0-9]+'
t_DOUBLE_STAR     = r'\*{2}'
t_STAR            = r'\*'
t_STRIKETHROUGH   = r'~~'
t_UNDERLINE       = r'\_{2}'
t_EXPOSANT        = r'\^'
t_INDICE          = r'\_'
t_LPARENTHESIS    = r'\('
t_RPARENTHESIS    = r'\)'
t_LBRACKET        = r'\['
t_RBRACKET        = r'\]'
t_BLOCKQUOTES     = r'(?m)^>'
t_CODE            = r'`'
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
    print(p[0])


def p_text(p):
    '''text : line
            | EMPTY_LINE'''
    p[0] = p[1]
    print(p[0])
    print(p[0])


def p_line_general(p):
    '''line : sentence EOL'''
    p[0] = p[1] + ' '
    print(p[0])


def p_sentence_complex(p):
    '''sentence : sentence sentence'''
    p[0] = p[1] + p[2]
    print(p[0])   


def p_sentence_word(p):
    '''sentence : WORD
                | SPACE'''
    p[0] = p[1]
    print(p[0])



def p_error(p):
    print("error %s" % p)
   

parser = yacc.yacc()

output = parser.parse(text)
print(output)


