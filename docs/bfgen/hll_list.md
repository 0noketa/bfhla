# list of high-level languages

## information

| name                                         | since | license      | author                                 |
| :------------------------------------------- | :---- | :----------- | :------------------------------------- |
| [iczelia/asmbf][as0]                         | 2017  | MIT          | iczelia(Kamila Szewczyk)               |
| [adam-mcdaniel/basm][ba0]                    | 2025  | MIT          | adam-mcdaniel                          |
| [elikaski/BF-it][bf0]                        | 2019  | MIT          | elikaski                               |
| [flynow10/bf-transpiler][bf1]                | 2026  | copyrighted  | flynow10                               |
| [benma/bfc][bf2]                             | 2013  | BSD-3-clause | benma                                  |
| [none-None1/BFFuck][bf3]                     | 2023  | CC0          | none-None1                             |
| [KrokodileGlue/bfm][bf4]                     | 2017  | MIT          | KrokodileGlue                          |
| [nicuveo/BFS][bf5]                           | 2018  | MIT          | nicuveo(Antoine Leblanc)               |
| [miggaz_elquez/brainfuck][br0]               | 2020? | copyrighted  | miggaz_elquez                          |
| [ogorodnikoff2012/brainfuck-assembler][br1]  | 2018  | BSD-2-clause | ogorodnikoff2012(Vladimir Ogorodnikov) |
| [Hixos/brainfuck-assembly][br2]              | 2023  | copyrighted  | Hixos(Luca Erbetta)                    |
| [vrighter/brainfuck-compiler][br3]           | 2011  | GPLv3        | vrighter                               |
| [redcrab2016/Brainfuck-Macro-Assembler][br4] | 2018  | GPLv3        | redcrab2016                            |
| [ImGajeed76/brainfuck_transpiler][br5]       | 2025  | GPLv3        | ImGajeed76                             |
| [hilmar-ackermann/brainfuckassembler][br6]   | 2019  | MIT          | Hilmar Ackermann                       |
| [BliepMonster/CBPP][cb0]                     | 2026  | copyrighted  | BliepMonster                           |
| [dumkin/ExLang2Bf][ex0]                      | 2019  | copyrighted  | dumkin                                 |
| [kmyk/forth-to-brainfuck][fo0]               | 2015  | MIT          | kmyk(Kimiyuki Onaka)                   |
| [Heathcorp/Mastermind][ma0]                  | 2023  | MIT          | Heathcorp                              |
| [Aarav-g123/python2brainfuck][py0]           | 2026  | copyrighted  | Aarav-g123(Aarav Gupta)                |
| [roodni/reusable-bf][re0]                    | 2021  | copyrighted  | roodni                                 |
| [ZED.CWT/To BrainFuck Transpiler][to0]       | 2017  | spec         | ZED.CWT                                |
| [bdebowski/brainfuck-transpiler][to0i0]      | 2022  | copyrighted  | bdebowski                              |

... and more

## functionality  

| name                                         | inline bf | array  | 2d array | bool | str | macro | goto | callable | constexpr | comment | output size |
| :------------------------------------------- | :-------- | :----- | :------- | :--- | :-- | :---- | :--- | :------- | :-------- | :------ | :---------- |
| [iczelia/asmbf][as0]                         | yes       | yes    | no       | no   | no  | ?     | yes  | yes      | yes       | yes     | ?           |
| [adam-mcdaniel/basm][ba0]                    | no        | yes    | no       | no   | no  | no    | yes  | yes      | ?         | yes     | ?           |
| [elikaski/BF-it][bf0]                        | no        | yes    | yes      | yes  | no  | yes   | no   | no       | yes       | yes     | medium      |
| [flynow10/bf-transpiler][bf1]                | no        | no     | no       | no   | no  | no    | no   | no       | yes       | yes     | ?           |
| [benma/bfc][bf2]                             | no        | yes    | no       | no   | no  | yes   | no   | no       | ?         | yes     | medium      |
| [none-None1/BFFuck][bf3]                     | no        | yes    | no       | no   | no  | yes   | no   | no       | ?         | yes     | ?           |
| [KrokodileGlue/bfm][bf4]                     | no        | yes    | no       | no   | no  | yes   | no   | no       | yes       | yes     | medium      |
| [nicuveo/BFS][bf5]                           | yes       | ?      | ?        | ?    | ?   | ?     | ?    | ?        | ?         | yes     | ?           |
| [miggaz_elquez/brainfuck][br0]               | yes       | no     | no       | no   | no  | yes   | no   | no       | ?         | yes     | small?      |
| [ogorodnikoff2012/brainfuck-assembler][br1]  | ?         | ?      | ?        | ?    | ?   | ?     | yes  | yes      | ?         | yes     | ?           |
| [Hixos/brainfuck-assembly][br2]              | ?         | ?      | ?        | ?    | ?   | ?     | yes  | yes      | ?         | yes     | ?           |
| [vrighter/brainfuck-compiler][br3]           | no        | yes    | no       | no   | no  | yes   | no   | no       | yes       | yes     | medium      |
| [redcrab2016/Brainfuck-Macro-Assembler][br4] | no        | single | no       | no   | no  | yes   | no   | no       | ?         | yes     | large       |
| [ImGajeed76/brainfuck_transpiler][br5]       | no        | no     | no       | no   | no  | no    | no   | no       | ?         | yes     | ?           |
| [hilmar-ackermann/brainfuckassembler][br6]   | no        | single | no       | no   | no  | no    | yes  | yes      | ?         | yes     | ?           |
| [BliepMonster/CBPP][cb0]                     | ?         | no?    | no       | yes  | ?   | yes   | no   | no       | ?         | yes     | ?           |
| [dumkin/ExLang2Bf][ex0]                      | ?         | ?      | ?        | ?    | ?   | ?     | ?    | ?        | ?         | ?       | ?           |
| [kmyk/forth-to-brainfuck][fo0]               | yes       | ?      | no       | ?    | ?   | ?     | ?    | ?        | ?         | yes     | small?      |
| [Heathcorp/Mastermind][ma0]                  | yes       | yes    | yes      | ?    | ?   | yes   | no   | no       | ?         | yes     | ?           |
| [Aarav-g123/python2brainfuck][py0]           | ?         | ?      | ?        | ?    | ?   | ?     | ?    | ?        | ?         | yes     | ?           |
| [roodni/reusable-bf][re0]                    | ?         | ?      | ?        | ?    | ?   | yes   | no   | no       | ?         | yes     | small?      |
| [ZED.CWT/To BrainFuck Transpiler][to0]       | ?         | yes    | ?        | ?    | ?   | yes   | no   | no       | ?         | yes     | small?      |

[as0]: <https://github.com/iczelia/asmbf>
[ba0]: <https://github.com/adam-mcdaniel/basm>
[bf0]: <https://github.com/elikaski/BF-it>
[bf1]: <https://github.com/flynow10/bf-transpiler>
[bf2]: <https://github.com/benma/bfc>
[bf3]: <https://github.com/none-None1/BFFuck>
[bf4]: <https://github.com/KrokodileGlue/bfm/>
[bf5]: <https://github.com/nicuveo/BFS>
[br0]: <https://code.antopie.org/miggaz_elquez/brainfuck/>
[br1]: <https://github.com/ogorodnikoff2012/brainfuck-assembler>
[br2]: <https://github.com/Hixos/brainfuck-assembly>
[br3]: <https://code.google.com/archive/p/brainfuck-compiler/>
[br4]: <https://github.com/redcrab2016/Brainfuck-Macro-Assembler>
[br5]: <https://github.com/ImGajeed76/brainfuck_transpiler>
[br6]: <https://gitlab.com/hilmar-ackermann/brainfuckassembler>
[cb0]: <https://github.com/BliepMonster/CBPP>
[ex0]: <https://github.com/dumkin/ExLang2Bf>
[fo0]: <https://github.com/kmyk/forth-to-brainfuck>
[ma0]: <https://github.com/Heathcorp/Mastermind>
[py0]: <https://github.com/Aarav-g123/python2brainfuck>
[re0]: <https://github.com/roodni/reusable-bf>
[to0]: <https://www.codewars.com/kata/59f9cad032b8b91e12000035>
[to0i0]: <https://github.com/bdebowski/brainfuck-transpiler>

## kmyk/forth-to-brainfuck

### for kmyk/forth-to-brainfuck, my dummy LIFO-object(singleton second-stack) library

written at Jan, 2022. this code is CC0. file name is maybe "lifo.fs".  
memory layout: "forth-stack(push:->, pop:<-), empty-space, lifo".  
do not push many data when this library is active.  
API is from [forth.org](http://www.forth.org/svfig/Len/softstak.htm).  

``` fs
( single lifo  adr = 0 )

: lifo ( n -- adr )
    \ FORTH  n = size of lifo
    \ this  n = reserved / 4 - 2
    s` ![>+<-]+>[[>>>>+<<<<-]>>>>-]>>+`
    s` <+[<[>-<-]>[<+>-]<]!`
;
: pop ( lifo -- n )
    s` !+>+[>[<->-]<[>+<-]>]`
    s` >[<+>-]+<<+[<[>-<-]>[<+>-]>[<+>-]<<]`
    s` >[<+>-]<!`
;
: push ( n lifo -- )
    s` !<[>+<-]+>>+[>[<->-]<[>+<-]<[>+<-]>>]`
    s` <[>+<-]+`
    s` <+[<[>-<-]>[<+>-]<]<!`
;
: pclear ( lifo -- )
    s` !+>+[>[<->-]<[>+<-]>]`
    s` +[<[>-<-]>[<+>-]<]<!`
;
```
