# bfhla

yet another High-level assembler/disassembler for Brainfuck. successor of [this project][_0noketa_tobf].

[_0noketa_tobf]: <https://github.com/0noketa/tobf>

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
* correct address even if just after not balanced loops.

### disassembler

it slightly reduces difficulty to read and modify some short existent Brainfuck programs.
