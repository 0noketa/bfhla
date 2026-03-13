# list of Brainfuck assembly languages (class 0s)

no simulation required. can not express some Brainfuck programs.  

## functionality

| name                                    | inline bf | var | macro | abs addr | rel addr | comment | macro instruction             | builtin struct |
| :-------------------------------------- | :-------- | :-- | :---- | :------- | :------- | :------ | :---------------------------- | :------------- |
| [waffelz0/BFASM][b0]                    | no        | yes | no    | via var  | no       | ?       | mul,div,cmp                   | tmp            |
| [Riven-Spell/bfasm][b1]                 | yes       | yes | no    | yes      | no       | ?       | copy?,mul,div,str_io,str_init | tmp            |
| [0noketa/tobf][t0]                      | yes       | yes | yes   | yes      | no       | yes     | copy,ifelse                   | tmp,arr,stk    |

[b0]: #waffelz0bfasm
[b1]: riven-spellbfasm
[t0]: #0noketatobf

## waffelz0/BFASM

waffelz0, other, 2025, ([source][url/waffelz0/BFASM])

[url/waffelz0/BFASM]: <https://github.com/waffelz0/BFASM>

## Riven-Spell/bfasm

Riven-Spell, MIT, 2017, ([source][url/Riven-Spell/bfasm])

[url/Riven-Spell/bfasm]: <https://github.com/Riven-Spell/bfasm/>

## 0noketa/tobf

0noketa, public domain, 2020?, ([source][url/0noketa/tobf])

[url/0noketa/tobf]: <https://github.com/0noketa/tobf/>
