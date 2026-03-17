# list of Brainfuck assembly languages (class 0s)

no simulation required. can not express some Brainfuck programs.  

## functionality

| name                                    | inline bf | var | macro | abs addr | rel addr | comment | macro instruction             | builtin struct |
| :-------------------------------------- | :-------- | :-- | :---- | :------- | :------- | :------ | :---------------------------- | :------------- |
| [waffelz0/BFASM][bf0]                   | no        | yes | no    | via var  | no       | ?       | mul,div,cmp                   | tmp            |
| [Riven-Spell/bfasm][bf1]                | yes       | yes | no    | yes      | no       | ?       | copy?,mul,div,str_io,str_init | tmp            |
| [MarMareDv/Brainfuckpp][br0]            | no        | yes | yes   | yes      | no       | Yes     | copy,mul                      | ?              |
| [0noketa/tobf][to0]                     | yes       | yes | yes   | yes      | no       | yes     | copy,ifelse                   | tmp,arr,stk    |

[bf0]: #waffelz0bfasm
[bf1]: #riven-spellbfasm
[br0]: #marmaredvbrainfuckpp
[to0]: #0noketatobf

## waffelz0/BFASM

waffelz0, other, 2025, ([source][url/waffelz0/BFASM])

[url/waffelz0/BFASM]: <https://github.com/waffelz0/BFASM>

## Riven-Spell/bfasm

Riven-Spell, MIT, 2017, ([source][url/Riven-Spell/bfasm])

[url/Riven-Spell/bfasm]: <https://github.com/Riven-Spell/bfasm/>

## MarMareDv/Brainfuckpp

MarMareDv, CC0, 2023, ([source][url/MarMareDv/Brainfuckpp])

[url/MarMareDv/Brainfuckpp]: <https://github.com/MarMareDv/Brainfuckpp/>

## 0noketa/tobf

0noketa, public domain, 2020, ([source][url/0noketa/tobf])

[url/0noketa/tobf]: <https://github.com/0noketa/tobf/>
