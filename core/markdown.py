import aemarkdown.inline as inline
import aemarkdown.block as block

text = '''# Sli is a perl wizard
## hello
### yy
#### pppp
test
this is a test 

1 beware
1 the 
1 ordered
1 list

> blockquoted
> as
> hell

```
THIS IS A CODE BLOCK
PROVIDED
BY
*SLI*
```


Sli is a ~bad programmer~ **very good programmer** *yes*
Sli **sucks**

* SLI
* STOP
* LOOKING
* AT
* MY
* SCREEN 


* oOo


__underlined text__
Hello ima *faggot* ^exposant^ _underline_

`hello ima code`

`hello ime *troll* code`'''

print(text)

blockOutput = block.blockParser(text)
finalOutput = inline.inlineParser(blockOutput)

print(finalOutput)
