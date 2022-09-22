from dataclasses import dataclass
from typing import Callable

from parsers import BaseParser
from operation.operator import BaseOperator
import utils

@dataclass
class Mutator:
    function: Callable[..., tuple[BaseOperator]] 
    ops: list[BaseOperator] | None # if None, then no mutation should take place

class Program:
    parser: BaseParser
    mutators: list[Mutator]

    def __init__(self, parser: BaseParser):
        self.parser = parser
        self.mutators = []
    
    def mutator(self, *ops: BaseOperator):
        if len(ops) == 0:
            raise ValueError('You must match at least one operator.')
        
        def decorator(function):
            self.mutators.append(Mutator(function, ops))
            return function
        
        return decorator

    def mutate(self):
        pass

    def compile(self) -> bytes:
        return b'TODO'

    def save(self, where: utils.file.Writable):
        utils.file.write(where, self.compile())
