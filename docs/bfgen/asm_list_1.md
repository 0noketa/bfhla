# list of Brainfuck assembly languages (class 1)

any simulation required.  

## functionality

| name                                    | inline bf | var | macro | abs addr | rel addr | comment | macro instruction      | builtin struct |
| :-------------------------------------- | :-------- | :-- | :---- | :------- | :------- | :------ | :--------------------- | :------------- |
| [AssemblerFuck++][a0]                   | no        | no  | no    | no       | yes      | no      | if                     | tmp            |

[a0]: #assemblerfuck

## AssemblerFuck++

Esolang1, public domain, 2022, spec, [source][url/assemberfuck++]

``` txt
UNTIL 4
    MOV RIGHT, P
    MOV P, IN
    MOV P, OUT
    MOV LEFT, P
    ADD 1
END
```

``` bf
----[++++>,.<+----]  if assembler can remove unused builtin structures
```

[url/assemberfuck++]: <https://esolangs.org/wiki/AssemblerFuck%2B%2B>
