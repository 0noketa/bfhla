# list of Brainfuck assembly languages (class 0)

no simulation required. all structures/objects are optional and/or with consistent ABI.  

## information

| name                                     | since | license       | language | author                |
| :--------------------------------------- | :---- | :------------ | :------- | :-------------------- |
| [AssemblerFuck][as0]                     | 2016  | public domain | spec     | Sesshomariu           |
| [Stalis/bf-asm][bf0]                     | 2018? | Apache        | Ruby     | Stalis                |
| [ethandhunt/bfa][bf1]                    | 2022  | copyrighted   | Python   | ethandhunt            |
| [piirios/BFIL][bf2]                      | 2023  | copyrighted   | Rust     | piirios               |
| [nthnn/Brainfuck Assembly Language][br0] | 2024  | MIT           | C++      | nthnn(Nathanne Isip)  |
| [Geometer1729/BrainFucktion][br1]        | 2019  | copyrighted   | Haskell  | Geometer1729          |
| [yeetree/FZCC/BrainFuzz][br2]            | 2023  | GPL           | C++      | yeetree               |
| [snuggyizme/Cortex][co0]                 | 2026  | MIT           | Python   | snuggyizme            |
| [pikhq/pebble][pe0]                      | 2007  | GPLv3         | Tcl      | pikhq(Ada Worcester)  |
| [MrRare2/readable_brainfuck][re0]        | 2024  | public domain | spec     | MrRare2               |
| [MrRare2/readable_brainfuck][re0]        | 2024  | GPLv3         | Python   | MrRare2               |

## functionality

| name                                     | inline bf | var | macro | abs addr | rel addr | comment | temporary | constraint/contract |
| :--------------------------------------- | :-------- | :-- | :---- | :------- | :------- | :------ | :-------- | :------------------ |
| [AssemblerFuck][as0]                     | no        | no  | no    | no       | yes      | no      | no        | no                  |
| [Stalis/bf-asm][bf0]                     | yes       | no  | no    | ?        | yes      | yes     | ?         | ?                   |
| [ethandhunt/bfa][bf1]                    | ?         | ?   | ?     | ?        | ?        | ?       | ?         | ?                   |
| [piirios/BFIL][bf2]                      | ?         | no  | yes   | yes      | yes      | ?       | ?         | ?                   |
| [nthnn/Brainfuck Assembly Language][br0] | ?         | no  | no    | ?        | yes      | no      | ?         | ?                   |
| [Geometer1729/BrainFucktion][br1]        | ?         | no  | yes   | yes      | ?        | ?       | ?         | ?                   |
| [yeetree/FZCC/BrainFuzz][br2]            | no        | no  | no    | no       | yes      | yes     | no        | no                  |
| [snuggyizme/Cortex][co0]                 | no        | yes | yes   | yes      | yes      | yes     | fixed?    | ?                   |
| [pikhq/pebble][pe0]                      | yes       | yes | yes   | yes      | yes      | yes     | explicit  | yes                 |
| [MrRare2/readable_brainfuck][re0]        | ?         | ?   | ?     | ?        | ?        | ?       | ?         | ?                   |

[as0]: #assemblerfuck
[bf0]: #stalisbf-asm
[bf1]: <https://github.com/ethandhunt/bfa>
[bf2]: #piiriosbfil
[br0]: #nthnnbrainfuck-assembly-language
[br1]: <https://github.com/Geometer1729/BrainFucktion>
[br2]: #yeetreefzccbrainfuzz
[co0]: #snuggyizmecortex
[re0]: #mrrare2readable_brainfuck
[pe0]: <https://github.com/pikhq/pebble>

## [AssemblerFuck](<https://esolangs.org/wiki/AssemblerFuck>)

``` txt
ADD 4
UNTIL 0
    MOV RIGHT, P
    MOV P, IN
    MOV P, OUT
    MOV LEFT, P
    SUB 1
END
```

``` bf
++++[>,.<-]
```

## [Stalis/bf-asm](<https://github.com/Stalis/bf-asm/>)

``` txt
set 4
#loop
    @ 1
    #inline
        ,.
    #end
    @ -1
    dec 1
#end
```

``` bf
++++[>,.<-]
```

## [piirios/BFIL](<https://github.com/piirios/BFIL>)

``` txt
add(33)
right(1)
add(4)
loop {
    left(2)
    print()
    right(2)
    sub(1)
}
```

or  

``` txt
add(33)
goto(1)
add(4)
loop {
    goto(0)
    print()
    goto(1)
    sub(1)
}
```

``` bf
+++++ +++++ +++++ +++++ +++++ +++++ +++ >++++[<.>-]
```

no input?  

## [nthnn/Brainfuck Assembly Language](<https://github.com/nthnn/brainfuck-assembly/>)

``` txt
mov dat, 4
jump begin
    inc ptr
    in
    out
    dec ptr
    dec dat
jump end
```

``` bf
++++[>,.<-]
```

## [yeetree/FZCC/BrainFuzz](<https://github.com/yeetree/FZCC>)

``` txt
add, 4;
loop;
    left, 1;
    in; out;
    right, 1;
    sub, 1;
end;
```

``` bf
++++[>,.<-]
```

## [snuggyizme/Cortex](<https://github.com/snuggyizme/Cortex/>)

``` txt
inc 4
lop
    lft 1
    inp
    prt
    rgt 1
    dec 1
end
```

or  

``` txt
let x 0
let y 1
fly x
set 4
lop
    fly y
    inp
    prt
    fly x
    dec 1
end
```

``` bf
++++[>,.<-]
```

"cpy"/"add" copy source, do not drain.  
"prn" uses BF-extension "P" (print int).  
temporaries are placed on address <0.  
clean output.  

## [MrRare2/readable_brainfuck][url/MrRare2/readable_brainfuck]  

[implementation][url/MrRare2/readable_brainfuck/impl]  

[url/MrRare2/readable_brainfuck]: <https://esolangs.org/wiki/Readable_Brainfuck>
[url/MrRare2/readable_brainfuck/impl]: <https://github.com/MrRare2/readable_brainfuck>
