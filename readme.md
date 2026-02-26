# bfhla

yet another high-level assembler/disassembler for Brainfuck. successor of [this project][_0noketa_tobf].

current version is mess and less featured stub.

[_0noketa_tobf]: <https://github.com/0noketa/tobf>

## language

### scope ([ <const_int> ]) (@ (<const_int>|<scope_name>) + <const_int>) = <var_decl_list>

define scope.

``` txt
scope scope0 = a, b, c
scope scope1[256] = d, e, f  # reserves 256 cells.
scope scope2 @ 0 = a2, b2, c2
scope scope3 @ scope0 + 1 = b3, c3  # not implemented. relative address as base address.
scope scope4 @ ? + 0 = v0, v1  # not implemented. current address as base address.
```

### move <dst_list> = <const_expr>

BF-styled assignment with drain. keyword "move" can be omitted.

``` txt
a = b  # with zero clear.
a+ = b  # without zero clear.
a- = b  # subtraction. without zero clear.
a+3 = b  # "a+=b*3; b=0;" in C. without zero clear.
a+, b-2, c+3 = d  # destinations with different multipliers.
move a = b  # explicitly keyworded.
```

### copy <dst_list> = <const_expr>

not implemented.

### balanced_loop_at <var_name>

this loop keeps pointer when leave.

### ifnz <var_name>

"[ code [-]]".

### predec_for <var_name>

"[- code ]".

### postdec_for <var_name>

"[ code -]".

### loop

raw "[".

### balanced_loop

raw "[". this loop keeps pointer when leave.

### end

end of any block.

### at <const_int>

move pointer.

``` txt
at 0  # not implemented. "p = &mem[0]" if available.
at +1  # >
at -1  # <
```

### skipr <const_int>

"[ >n ]".

### skipl <const_int>

decremental version of skipr.

### bf <const_str>

inline BF-RLE(suffix).

``` txt
bf "+4 [ >2 ,.[-] <2 -]"
```

## difference to tobf

### somehow better language, analyser and IR

tobf:

``` txt
c d n x y z

input c
copy c d

sub 64 d
if d
    set 1 n
endif d

sub 65 c
if c
    set 2 n
endif c

# x = n; y += n; z += n * 2; n = 0;
move n x +y +z +z 
```

bfhla:

``` txt
# every assignment can ommit keyword.
config assign_method = move
# every scope can start at any address
scope mem @ 0 = c, d, n, x, y, z

input c
# this copy will use n as temporary
copy d = c

d- = 64
ifnz d
    n = 1
end  # bfhla can recognize blocks

c- = 65
ifnz c
    n = 2
end

# bfhla can describe "move" macro-instruction with any memory-map without strange format such as repeated same destination name.
# x = n; y += n; z += n * 2; n = 0;
x, y+, z+2 = n
```

### automated temporary assignment

no specified variable is required. you just prepare variables, any free variable known as zero will be used.

### more semantic informations

you can notice assembler:

* is a loop balanced or not.  
* correct address. even if just after not balanced loops.

### disassembler

sometimes it slightly reduces difficulty to read and modify some short existent Brainfuck programs.
