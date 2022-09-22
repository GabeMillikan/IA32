from .operand import register as reg

class BaseOperator:
    pass

class Move(BaseOperator):
    mnemonic = 'MOV'

class Push(BaseOperator):
    mnemonic = 'PUSH'

class Pop(BaseOperator):
    mnemonic = 'POP'
