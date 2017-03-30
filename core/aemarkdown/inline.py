import ply.lex as lex
import ply.yacc as yacc

def inlineParser(text):

    if text[-1] != '\n':
        text = text + "\n"


    tokens = (
        'ESCAPE', 
        'CODE', 
        'CODE_BLOCK',
        'EMPTY_LINE',
        'EOL',
        'HEADER',
        'UNORDERED_LIST',
        'ORDERED_LIST',
        'SEMPHASIS',
        'LEMPHASIS', 
        'STRIKETHROUGH',
        'UNDERLINE', 
        'EXPOSANT', 
        'INDICE', 
        'LPARENTHESIS', 
        'RPARENTHESIS',
        'LBRACKET',
        'RBRACKET',
        'BLOCKQUOTE', 
        'SPACE', 
        'WORD', 
        'OTHER',
    )


    #Rules
    t_ESCAPE          = r'\\'
    t_CODE_BLOCK      = r'^```(.|\n)*?^```\n'
    t_CODE            = r'`.*?`'
    t_EMPTY_LINE      = r'(?m)^\n'
    t_EOL             = r'\n'
    t_HEADER          = r'(?m)^\#+'
    t_UNORDERED_LIST  = r'(?m)^\*\ '
    t_ORDERED_LIST    = r'(?m)^1\ '
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
    t_BLOCKQUOTE      = r'(?m)^>\ '
    t_SPACE           = r'\ '
    t_WORD            = r'\b\S+\b'
    t_OTHER           = r'.'


    def t_error(t):
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
                | header_line
                | unordered_list
                | ordered_list
                | blockquote
                | CODE_BLOCK'''
        p[0] = p[1]


    def p_text_empty_line(p):
        '''text : EMPTY_LINE'''
        p[0] = "\n</br>\n"


    def p_line_general(p):
        '''line : sentence EOL'''
        p[0] = p[1] + ' '


    #multiline
    def p_blockquote(p):
        '''blockquote : BLOCKQUOTE sentence EOL'''
        p[0] = "<blockquote>" + p[2] + "</blockquote>" + p[3]


    def p_unordered_list(p):
        '''unordered_list : UNORDERED_LIST sentence EOL'''
        p[0] = "<li>" + p[2] + "</li>" + p[3]

    def p_ordered_list(p):
        '''ordered_list : ORDERED_LIST sentence EOL'''
        p[0] = "<li>" + p[2] + "</li>" + p[3]


    def p_header_line(p):
        '''header_line : HEADER sentence EOL'''

        if p[2][0] == " ": #remove unecessary first space on title
            p[2] = p[2][1:]

        p[0] = "<h" + str(len(p[1]))  + ">" + p[2] + "</h" + str(len(p[1]))  + ">" + p[3] #dynamic title composition


    #inline
    def p_sentence_complex(p):
        '''sentence : sentence sentence'''
        p[0] = p[1] + p[2]


    def p_sentence_stong_emphasis(p):
        '''sentence : SEMPHASIS'''
        p[0] = "<b>" + p[1][2:-2] + "</b>"

    def p_sentence_light_emphasis(p):
        '''sentence : LEMPHASIS'''
        p[0] = "<em>" + p[1][1:-1] + "</em>"

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
        p[0] = "<pre><code>" + p[1][1:-1] + "</code></pre>"


    def p_sentence_word(p):
        '''sentence : WORD
                    | SPACE
                    | OTHER'''
        p[0] = p[1]



    def p_error(p):
        print("error %s" % p)
       

    parser = yacc.yacc()

    output = parser.parse(text)
    
    return output;
