# list of Brainfuck preprocessors

## functionality

| name                                    | var | macro | block mac | mac in mac | param | comment | others        | include |
| :-------------------------------------- | :-- | :---- | :-------- | :--------- | :---- | :------ | :------------ | :------ |
| [hagyu-aya/bf-generator][b0]            | no  | no    | no        | no         | no    | no      | dup           | no      |
| [AAlx0451/bfc/BFpp][b1]                 | no  | yes   | yes       | yes        | yes   | yes     | block_dup     | yes     |
| [xeniagda/lldbf/bfpp][b2]               | yes | yes   | yes       | yes        | yes   | yes     | ?             | yes     |
| [cornwarecjp/brainfuck-macros][b3]      | ?   | ?     | ?         | ?          | ?     | ?       | ?             | ?       |
| [Jorgeromeu/brainfuck-preprocessor][b4] | ?   | ?     | ?         | ?          | ?     | ?       | ?             | ?       |
| [Pi-Man/Brainfuck-Preprocessor][b5]     | ?   | ?     | ?         | ?          | ?     | ?       | ?             | ?       |
| [ebf][e0]                               | ?   | ?     | ?         | ?          | ?     | ?       | ?             | ?       |
| [AurelienMoisson/macro-brainfuck][m0]   | no  | yes   | no        | no         | no    | no      | no            | no      |
| [vs-123/mbf][m1]                        | no  | yes   | yes       | yes        | no    | yes     | no            | no      |

[b0]: #hagyu-ayabf-generator
[b1]: #aalx0451bfcbfpp
[b2]: #xeniagdalldbfbfpp
[b3]: #cornwarecjpbrainfuck-macros
[b4]: #jorgeromeubrainfuck-preprocessor  
[b5]: #pi-manbrainfuck-preprocessor
[e0]: #ebf
[m0]: #aurelienmoissonmacro-brainfuck
[m1]: #vs-123mbf

## hagyu-aya/bf-generator

hagyu-aya, copyrighted, 2020, C++ ([source][url/hagyu-aya/bf-generator])  

extended BF-RLE  

[url/hagyu-aya/bf-generator]: <https://github.com/hagyu-aya/bf-generator>

## AAlx0451/bfc/BFpp

AAlx0451, public domain, 2026?, C ([source][url/bfpp])  

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

[url/bfpp]: <https://github.com/AAlx0451/bfc>

## xeniagda/lldbf/bfpp

xeniagda(xenia), copyrighted, 2019, Python ([source][url/xeniagda/lldbf/bfpp])  

[url/xeniagda/lldbf/bfpp]: <https://github.com/xeniagda/lldbf>

## cornwarecjp/brainfuck-macros

cornwarecjp, GPLv3, 2018, Python ([source][url/cornwarecjp/brainfuck-macros])  

[url/cornwarecjp/brainfuck-macros]: <https://github.com/cornwarecjp/brainfuck-macros>

## Jorgeromeu/brainfuck-preprocessor

Jorgeromeu, MIT, 2021, Python ([source][url/Jorgeromeu/brainfuck-preprocessor])  

[url/Jorgeromeu/brainfuck-preprocessor]: <https://github.com/Jorgeromeu/brainfuck-preprocessor>

## Pi-Man/Brainfuck-Preprocessor

Pi-Man, MIT, 2023, C ([source][url/Pi-Man/Brainfuck-Preprocessor])  

[url/Pi-Man/Brainfuck-Preprocessor]: <https://github.com/Pi-Man/Brainfuck-Preprocessor>

## ebf

westerp, GPLv3, 2010?, Brainfuck(with preprocessor)  ([source][url/ebf])  

[url/ebf]: <https://github.com/westerp/ebf-compiler>

## AurelienMoisson/macro-brainfuck

AurelienMoisson, copyrighted, 2019, Brainfuck(with preprocessor) ([source][url/AurelienMoisson/macro-brainfuck])  

``` txt
:c[-]
:e,.
c++++[>e<-]
```

``` bf
[-]++++[>,.<-]
```

[url/AurelienMoisson/macro-brainfuck]: <https://github.com/AurelienMoisson/macro-brainfuck>

## vs-123/mbf

vs-123, AGPLv3, 2025, C ([source][url/vs-123/mbf])  

[url/vs-123/mbf]: <https://github.com/vs-123/mbf>
