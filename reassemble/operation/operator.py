from .operand import register as reg

def operator(mnemonic):
    def decorator(cls):
        cls.mnemonic = mnemonic
        return cls
    return decorator

@operator('MOV')
class Move:
    pass

