import ply.lex as lex
import ply.yacc as yacc

def blockParser(text):

    if text[-1] != '\n':
        text = text + "\n"

    #lexer
    tokens = (
        'CODE_BLOCK',
        'HEADER',
        'UNORDERED_LIST',
        'ORDERED_LIST',
        'BLOCKQUOTE',
        'TABLE_HEADER',
        'TABLE_CONTENT',
        'EMPTY_LINE',
        'PARAGRAPH',
    )

    #lexer rules
    t_CODE_BLOCK       = r'^```(.|\n)*?^```'
    t_HEADER           = r'(?m)^\#+'
    t_UNORDERED_LIST   = r'(?m)^(\*.*?\n)+'
    t_ORDERED_LIST     = r'(?m)^([0-9]+.*?\n)+'
    t_BLOCKQUOTE       = r'(?m)^(>\ .*?\n)+'
    t_TABLE_HEADER     = r'(?m)^\|.+\|\n\|-.*?\n'
    t_TABLE_CONTENT    = r'(?m)(^\|.+?\|\n)+'
    t_EMPTY_LINE       = r'(?m)^\n'
    t_PARAGRAPH        = r'(?m)^(.+?\n)+'


    def t_error(t):
        t.lexer.skip(1)

    lexer = lex.lex()
    lexer.input(text)

    while True:
        tok = lexer.token()
        if not tok:
            break
        print(tok)


    #parser
    def p_text_complex(p):
        '''text : text text'''
        p[0] = p[1] + p[2]

    def p_text(p):
        '''text : code_block
                | HEADER
                | unordered_list_block
                | ordered_list_block
                | blockquote
                | empty_line
                | table_header
                | table_content
                | paragraph'''
        p[0] = p[1]


    def p_code_block(p):
        '''code_block : CODE_BLOCK'''
        p[0] = "<pre><code>" + p[1][3:-4] + "\n</code></pre>"


    def p_ordered_list_block(p):
        '''ordered_list_block : ORDERED_LIST'''
        p[0] = "<ol>\n" + p[1] + "</ol>\n"

    def p_unordered_list_block(p):
        '''unordered_list_block : UNORDERED_LIST'''
        p[0] = "<ul>\n" + p[1] + "</ul>\n"

    def p_blockquote(p):
        '''blockquote : BLOCKQUOTE'''
        p[0] = "<blockquote>\n" + p[1] + "</blockquote>\n"

    def p_table_header(p):
        '''table_header : TABLE_HEADER'''
        p[0] = "<table>\n" + p[1]

    def p_table_content(p):
        '''table_content : TABLE_CONTENT'''
        p[0] = p[1] + "\n</table>"

    def p_paragraph(p):
        '''paragraph : PARAGRAPH'''
        p[0] = "<p>\n" + p[1] + "\n</p>"
    

    #def p_paragraph_complex(p):
    #    '''paragraph : paragraph paragraph'''
    #    p[0] = p[1] + p[2]


    #def p_paragraph(p):
        #'''paragraph : LINE'''
        #p[0] = p[1]

    def p_empty_line(p):
        '''empty_line : EMPTY_LINE'''
        p[0] = "</br>\n"

    def p_error(p):
        print("error %s" % p)

    parser = yacc.yacc()
    output = parser.parse(text)

    print(output)
    return output
