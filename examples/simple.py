from swallowtail.operation import operator as op
from swallowtail import parsers
from swallowtail.program import Program

image = Program(parsers.EXE('examples/HelloWorld_x86.exe'))

'''
this instruction:
MOV dst, src

is equivalent to these instructions:
PUSH src
POP dst

but both operations have entirely different binary signatures.
'''
@image.mutator(op.Move)
def mov_to_pushpop(mov):
    return (
        op.Push(mov.src),
        op.Pop(mov.dst)
    )

'''
Same idea as above, but backwards.
'''
@image.mutator(op.Push, op.Pop)
def pushpop_to_mov(push, pop):
    return (
        op.Move(src=push.target, dst=pop.target)
    )

stats = image.mutate()
image.save('modified.exe')

print(stats.prettify())
# ^ shows details about:
# - how many mutations occurred
# - how much code is left unchanged
# - where there are opportunities for more mutations (i.e. where there are long sequences of unmutated code)
# - ... and tons of other stuff
