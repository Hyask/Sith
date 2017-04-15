import core.aemarkdown.inline as inline
import core.aemarkdown.block as block
#import aemarkdown.block as block

text = '''
KnotawordK
this is a link http://link huhu
this is a named link [named](http://www.SliSux.com) k


# Title 1

## Title 2

### Title 3



this is a normal paragraph


1 this
2 is
15 an
254 ordered **iekde** list

> this is a blockquoted
> text

```
THIS IS A CODE BLOCK
Nothing is **interpreted** here
```


Inline test : ~Strikethrough~ *emphasis* **double emphasis** ^exposant^ _indice_ __underlined__

* an
* unordered
* list

text inside code `code`

| Titre1 | Titre2 | Titre3 |
|--------|--------|--------|
| test   | test   | test   |

Vous pouvez le faire en priori
Il y'a aussi des MaKrons'''

atext='''#zepoezkf

* fff
* vfff
* ffff

zfref
rfref
erfef'''

def markdown(text):

    #print(text)

    finalOutput = block.blockParser(text)

    #print(finalOutput)

    return finalOutput


if __name__ == "__main__":


    print(text)

    finalOutput = block.blockParser(text)

    print(finalOutput)
