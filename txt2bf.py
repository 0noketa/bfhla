
# text to loop-less Brainfuck
import sys


def log(s: str):
    # sys.stderr.write(s + "\n")
    pass


src = [*map(ord, "".join(sys.stdin.readlines()))]

ks = list(set(src))
usage = {}
use2key = {}
for k in ks:
    v = len([i for i in src if i == k])

    usage[k] = v
    if not v in use2key:
        use2key[v] = []

    use2key[v].append(k)

sys.stderr.write(f"src size: {len(src)}\n")
log(f"char types: {len(ks)}")

for i in sorted(use2key.keys())[-4:]:
    log(f"  {i} times: {' '.join(map(str, use2key[i]))}")

ss = []
for rate in (0.02, 0.03, 0.05, 0.08, 0.1):
    log(f"rate {rate}")

    priority = reversed(sorted(use2key.keys()))
    memo_dpt = 0
    for i in priority:
        if i < len(src) * rate:
            break
        memo_dpt += 1

    memo = []
    if memo_dpt:
        log(f"  better for memo: {memo_dpt}")
        for i in sorted(use2key.keys())[-memo_dpt:]:
            log(f"    {i} times: {' '.join(map(str, use2key[i]))}")
            memo.extend(use2key[i])

    s = ""

    for i, v in enumerate(memo):
        s += (">" + "+" * v)
    s += ("<" * len(memo))

    it = 0
    p = 0
    for c in src:
        v_diff = abs(c - it)

        if c in memo:
            idx = memo.index(c) + 1
            diff = abs(p - idx)
            if diff < v_diff + p:
                if p < idx:
                    s += (">" * diff + ".")
                else:
                    s += ("<" * diff + ".")
                p = idx
                continue
        
        if p != 0:
            s += ("<" * p)
            p = 0

        if it < c:
            s += ("+" * v_diff + ".")
        else:
            s += ("-" * v_diff + ".")
        it = c

    ss.append(s)
    log(f"  output: {len(s)}")


ss.sort(key=len)

s = ss[0]
for i in range(0, len(s), 80):
    print(s[i:i + 80])

sys.stderr.write(f"dst size: {len(s)}\n")
