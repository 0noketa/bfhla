# list of Brainfuck preprocessors

## information

| name                                     | since | license       | language   | author            |
| :--------------------------------------- | :---- | :------------ | :--------- | :---------------- |
| [hagyu-aya/bf-generator][bf0]            | 2020  | copyrighted   | C++        | hagyu-aya         |
| [BFC/BFA][bf1]                           | 2004  | GPLv2         | C          | Clifford Wolf     |
| [AAlx0451/bfc/BFpp][bf2]                 | 2026  | public domain | C          | AAlx0451          |
| [xeniagda/lldbf/bfpp][bf3]               | 2019  | copyrighted   | Python     | xeniagda(xenia)   |
| [WilliamDann/bpp][bp0]                   | 2021  | copyrighted   | Python     | WilliamDann       |
| [cornwarecjp/brainfuck-macros][br0]      | 2018  | GPLv3         | Python     | cornwarecjp       |
| [Jorgeromeu/brainfuck-preprocessor][br1] | 2021  | MIT           | Python     | Jorgeromeu        |
| [Pi-Man/Brainfuck-Preprocessor][br2]     | 2023  | MIT           | C          | Pi-Man            |
| [ebf][eb0]                               | 2010  | GPLv3         | Brainfuck  | westerp           |
| [AurelienMoisson/macro-brainfuck][ma0]   | 2019  | copyrighted   | Brainfuck  | AurelienMoisson   |
| [vs-123/mbf][mb0]                        | 2025  | AGPLv3        | C          | vs-123            |
| [VilgotanL/Bf-Transpilers/vbf][vb0]      | 2021? | GPLv3         | JavaScript | VilgotanL         |

## functionality

| name                                     | var | macro | block mac | mac in mac | param | comment | others        | include |
| :--------------------------------------- | :-- | :---- | :-------- | :--------- | :---- | :------ | :------------ | :------ |
| [hagyu-aya/bf-generator][bf0]            | no  | no    | no        | no         | no    | no      | dup           | no      |
| [BFC/BFA][bf1]                           | yes | no    | no        | no         | no    | yes     | selector      | no?     |
| [AAlx0451/bfc/BFpp][bf2]                 | no  | yes   | yes       | yes        | yes   | yes     | block_dup     | yes     |
| [xeniagda/lldbf/bfpp][bf3]               | yes | yes   | yes       | yes        | yes   | yes     | ?             | yes     |
| [WilliamDann/bpp][bp0]                   | no  | yes   | yes       | ?          | yes   | ?       | ?             | yes     |
| [cornwarecjp/brainfuck-macros][br0]      | ?   | ?     | ?         | ?          | ?     | ?       | ?             | ?       |
| [Jorgeromeu/brainfuck-preprocessor][br1] | ?   | ?     | ?         | ?          | ?     | ?       | ?             | ?       |
| [Pi-Man/Brainfuck-Preprocessor][br2]     | ?   | ?     | ?         | ?          | ?     | ?       | ?             | ?       |
| [ebf][eb0]                               | ?   | ?     | ?         | ?          | ?     | ?       | ?             | ?       |
| [AurelienMoisson/macro-brainfuck][ma0]   | no  | yes   | no        | no         | no    | no      | no            | no      |
| [vs-123/mbf][mb0]                        | no  | yes   | yes       | yes        | no    | yes     | no            | no      |
| [VilgotanL/Bf-Transpilers/vbf][vb0]      | no  | no    | no        | no         | no    | yes     | if            | no      |

[bf0]: #hagyu-ayabf-generator
[bf1]: #bfcbfa
[bf2]: #aalx0451bfcbfpp
[bf3]: <https://github.com/xeniagda/lldbf>
[bp0]: #williamdannbpp
[br0]: <https://github.com/cornwarecjp/brainfuck-macros>
[br1]: <https://github.com/Jorgeromeu/brainfuck-preprocessor>  
[br2]: <https://github.com/Pi-Man/Brainfuck-Preprocessor>
[eb0]: #ebf
[ma0]: #aurelienmoissonmacro-brainfuck
[mb0]: <https://github.com/vs-123/mbf>
[vb0]: <https://github.com/VilgotanL/Bf-Transpilers>

## [hagyu-aya/bf-generator](<https://github.com/hagyu-aya/bf-generator>)

extended BF-RLE  

## [BFC/BFA](<http://www.clifford.at/bfcpu/>)

intermediate language of BFC.  
similar to pseudo-code some BF user use.  

``` txt
(x) (y) (z)  ; global var decl. this language has nestable scopes.
<x>  ; address selector
++++
[-
    <y>+
    <z>+
    ; at the block-end, restores pointer pointed to the var used for this block
]
```

## [AAlx0451/bfc/BFpp](<https://github.com/AAlx0451/bfc>)

``` txt
{F AT(P) {xP{>}}}
{F ENDAT(P) {xP{<}}}
{F FOR(P,X) AT(P)[-] {xX{+}} [ ENDAT(P)}
{F ENDFOR(P) AT(P) -] ENDAT(P)}
{F ECHO_AT(P) AT(P) ,. ENDAT(P)}
FOR(1, 4)
    ECHO_AT(2)
ENDFOR(1)
```

``` bf
>[-]++++[<>>,.<<>-]<
```

## [WilliamDann/bpp](<https://github.com/WilliamDann/bpp>)

macro processor + library as stack-based language.  
main program uses template-files as macro-functions with parameter.  

## ebf

[source][url/ebf]  

[url/ebf]: <https://github.com/westerp/ebf-compiler>

## AurelienMoisson/macro-brainfuck

[source][url/AurelienMoisson/macro-brainfuck]  

``` txt
:c[-]
:e,.
c++++[>e<-]
```

``` bf
[-]++++[>,.<-]
```

[url/AurelienMoisson/macro-brainfuck]: <https://github.com/AurelienMoisson/macro-brainfuck>
