from dataclasses import dataclass

@dataclass
class Register:
    name: str # EAX, ECX, etc.
    size: int # in bytes

EAX = Register('EAX', 4)
ECX = Register('ECX', 4)
