# list of Brainfuck assembly languages (class 0)

no simulation required.  

## functionality

| name                                    | inline bf | var | macro | abs addr | rel addr | comment | macro instruction              | builtin struct |
| :-------------------------------------- | :-------- | :-- | :---- | :------- | :------- | :------ | :----------------------------- | :------------- |
| [AssemblerFuck][a0]                     | no        | no  | no    | no       | yes      | no      | no                             | no             |
| [Stalis/bf-asm][b0]                     | yes       | no  | no    | ?        | yes      | yes     | copy?                          | no             |
| [ethandhunt/bfa][b1]                    | ?         | ?   | ?     | ?        | ?        | ?       | ?                              | ?              |
| [piirios/BFIL][b2]                      | ?         | no  | yes   | yes      | yes      | ?       | ?                              | ?              |
| [nthnn/Brainfuck Assembly Language][b3] | ?         | no  | no    | ?        | yes      | no      | no                             | no             |
| [Geometer1729/BrainFucktion][b4]        | ?         | no  | yes   | yes      | ?        | ?       | move,copy                      | no             |
| [snuggyizme/Cortex][c0]                 | no        | yes | yes   | yes      | yes      | yes     | clear,copy,int_out(bf_ext),cmp | tmp            |
| [MrRare2/readable_brainfuck][r0]        | ?         | ?   | ?     | ?        | ?        | ?       | ?                              | ?              |

[a0]: #assemblerfuck
[b0]: #stalisbf-asm
[b1]: #ethandhuntbfa
[b2]: #piiriosbfil
[b3]: #nthnnbrainfuck-assembly-language
[b4]: #geometer1729brainfucktion
[c0]: #snuggyizmecortex
[r0]: #mrrare2readable_brainfuck

## AssemblerFuck

Sesshomariu, public domain, 2016 ([spec][url/assemberfuck])  

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

[url/assemberfuck]: <https://esolangs.org/wiki/AssemblerFuck>

## Stalis/bf-asm

Stalis, Apache, 2018?, Ruby ([source][url/Stalis/bf-asm])  

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

[url/Stalis/bf-asm]: <https://github.com/Stalis/bf-asm/>

## ethandhunt/bfa

ethandhunt, copyrighted, 2022, Python ([source][url/ethandhunt/bfa])  

[url/ethandhunt/bfa]: <https://github.com/ethandhunt/bfa>

## piirios/BFIL

piirios, copyrighted, 2023, Rust ([source][url/piirios/BFIL])  

[url/piirios/BFIL]: <https://github.com/piirios/BFIL>

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

## nthnn/Brainfuck Assembly Language

nthnn(Nathanne Isip), MIT, 2024, C++ ([source][url/nthnn/brainfuck-assembly])  

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

[url/nthnn/brainfuck-assembly]: <https://github.com/nthnn/brainfuck-assembly/>

## Geometer1729/BrainFucktion

Geometer1729, copyrighted, 2019, Haskell ([source][url/Geometer1729/BrainFucktion])  

[url/Geometer1729/BrainFucktion]: <https://github.com/Geometer1729/BrainFucktion>

## snuggyizme/Cortex

snuggyizme, MIT, 2026, Python ([source][url/snuggyizme/Cortex])  

``` txt
inc 4
lop
    lft 1
    imp
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
    imp
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

[url/snuggyizme/Cortex]: <https://github.com/snuggyizme/Cortex/>

## MrRare2/readable_brainfuck

MrRare2, public domain, 2024 ([spec][url/MrRare2/readable_brainfuck])  
MrRare2, GPLv3, 2024, Python ([impl][url/MrRare2/readable_brainfuck/impl])  

[url/MrRare2/readable_brainfuck]: <https://esolangs.org/wiki/Readable_Brainfuck>
[url/MrRare2/readable_brainfuck/impl]: <https://github.com/MrRare2/readable_brainfuck>
