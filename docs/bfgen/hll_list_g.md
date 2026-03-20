# list of high-level languages (goto simulators)

implements explicit or implicit(as function) label/goto system.  

## information

| name                                         | since | license      | author                                 |
| :------------------------------------------- | :---- | :----------- | :------------------------------------- |
| [YaroslavGaponov/as2bf][as0]                 | 2021  | copyrighted  | YaroslavGaponov(Yaroslav Gaponov)      |
| [iczelia/asmbf][as2]                         | 2017  | MIT          | iczelia(Kamila Szewczyk)               |
| [adam-mcdaniel/basm][ba0]                    | 2025  | MIT          | adam-mcdaniel                          |
| [BFASM][bf3]                                 | 2004  | GPLv2        | Jeffry Johnston                        |
| [ogorodnikoff2012/brainfuck-assembler][br4]  | 2018  | BSD-2-clause | ogorodnikoff2012(Vladimir Ogorodnikov) |
| [Hixos/brainfuck-assembly][br5]              | 2023  | copyrighted  | Hixos(Luca Erbetta)                    |
| [hilmar-ackermann/brainfuckassembler][br9]   | 2019  | MIT          | Hilmar Ackermann                       |
| [EliiasG/BrainFuckPythonLang][br10]          | 2023  | copyrighted  | EliiasG                                |
| [cjxgm/brainsuck/llbs][br11]                 | 2012  | GPLv2        | cjxgm(Giumo Clanjor)(哆啦比猫/兰威举)  |
| [shinh/elvm][el0]                            | 2016  | MIT          | shin.h(Shinichiro Hamaji)              |
| [gXLg/tobf][to1]                             | 2022  | copyrighted  | gXLg                                   |
| [VilgotanL/Bf-Transpilers/vbf][vb0]          | ?     | GPLv3        | VilgotanL                              |

... and more

## functionality  

| name                                        | bf  | array  | stack | macro | goto | call | output size |
| :------------------------------------------ | :-- | :----- | :---- | :---- | :--- | :--- | :---------- |
| [YaroslavGaponov/as2bf][as0]                | ?   | ?      | ?     | ?     | yes  | yes  | ?           |
| [iczelia/asmbf][as2]                        | yes | yes    | ?     | ?     | yes  | yes  | ?           |
| [adam-mcdaniel/basm][ba0]                   | no  | yes    | ?     | no    | yes  | yes  | ?           |
| [BFASM][bf3]                                | ?   | single | ?     | no?   | yes  | yes  | large?      |
| [ogorodnikoff2012/brainfuck-assembler][br4] | ?   | ?      | ?     | ?     | yes  | yes  | ?           |
| [Hixos/brainfuck-assembly][br5]             | ?   | ?      | ?     | ?     | yes  | yes  | ?           |
| [hilmar-ackermann/brainfuckassembler][br9]  | no  | single | ?     | no    | yes  | yes  | ?           |
| [cjxgm/brainsuck/llbs][br11]                | ?   | single | ?     | no    | yes  | yes  | ?           |
| [shinh/elvm][el0]                           | ?   | ?      | ?     | ?     | yes  | yes  | large?      |
| [gXLg/tobf][to1]                            | ?   | yes    | ?     | yes   | ?    | yes  | ?           |
| [VilgotanL/Bf-Transpilers/vbf_3][vb0]       | ?   | ?      | ?     | ?     | yes  | no?  | ?           |

[as0]: <https://github.com/YaroslavGaponov/as2bf>
[as2]: <https://github.com/iczelia/asmbf>
[ba0]: <https://github.com/adam-mcdaniel/basm>
[bf3]: #bfasm
[br4]: <https://github.com/ogorodnikoff2012/brainfuck-assembler>
[br5]: <https://github.com/Hixos/brainfuck-assembly>
[br9]: <https://gitlab.com/hilmar-ackermann/brainfuckassembler>
[br10]: <https://github.com/EliiasG/BrainFuckPythonLang>
[br11]: <https://github.com/cjxgm/brainsuck>
[el0]: <https://github.com/shinh/elvm>
[to1]: <https://github.com/gXLg/tobf>
[vb0]: <https://github.com/VilgotanL/Bf-Transpilers>

## BFASM

C->self bootstrapped.  
  
bfasm-0.20.zip from [Brainfuck Archive][bfasm/link]  
md5: 7ece714a0827a6d2950922ea9e6a0acc  
sha256: 3d96bff383461872f8225ee03cf6400802e6f206e3bab0dc9b9591cf04c93b7d  

[bfasm/link]: <https://esoteric.sange.fi/brainfuck/utils/>
