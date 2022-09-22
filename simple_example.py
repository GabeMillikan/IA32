from swallowtail.operation import operator as op
from swallowtail import parsers
from swallowtail.program import Program

image = Program(parsers.DLL('env/Scripts/python.exe'))

'''
@image.mutator(op.Move)
def mov_to_pushpop(mov):
    return (
        op.Push(mov.src),
        op.Pop(mov.dst)
    )

@image.mutator(op.Push, op.Pop)
def pushpop_to_mov(push, pop):
    return (
        op.Move(src=push.target, dst=pop.target)
    )

image.mutate()
image.save('modified.exe')
'''

print(image.parser.prettify())
