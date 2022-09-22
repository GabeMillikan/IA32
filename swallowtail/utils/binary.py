import typing
import dataclasses
import struct

def extract(data: int, *groups: int) -> tuple[int, ...]:
    '''
    Extract groups of bits from an integer.

    >>> extract(0b11101010, 2, 3, 3) == (0b11, 0b101, 0b010)
    True

    >>> extract(0b00111000_11101010, 6, 4, 4, 2) == (0b001110, 0b0011, 0b1010, 0b10)
    True
    '''

    results: list[int] = []
    for group in reversed(groups):
        results.append(data & ((1 << group) - 1))
        data >>= group

    return tuple(reversed(results))

class StructuredField:
    size: int
    format: str

@dataclasses.dataclass
class StructureMetadata:
    size: int = 0
    format: str = '<'
    fields: list[tuple[str, int]] = dataclasses.field(default_factory=list)

T = typing.TypeVar('T')
class Structure:
    '''
    >>> class Test(Structure):
    ...     x: BYTE
    ...     y: CHAR
    ...     z: DWORD
    ...     w: list[CHAR] = ARRAY(3)
    ...     p: bytes = STRING(11)
    ...
    >>> Test._metadata.size
    20
    >>> Test._metadata.format
    '<BcL3c11s'
    >>> Test(b'x')
    Traceback (most recent call last):
    ...
    ValueError: This structure requires exactly 20 bytes, but you provided 1.
    >>> t = Test(b'\\xFFH\\x05\\x00\\x00\\x00ABCHELLO WORLD')
    >>> t.x, t.y, t.z, t.w, t.p
    (255, b'H', 5, [b'A', b'B', b'C'], b'HELLO WORLD')
    '''

    def __init__(self, data: bytes):
        if self._metadata.size != len(data):
            raise ValueError(f'This structure requires exactly {self._metadata.size} bytes, but you provided {len(data)}.')
        
        unpacked = list(struct.unpack(self._metadata.format, data))
        for name, grouping in self._metadata.fields:
            if grouping > 1:
                setattr(self, name, unpacked[:grouping])
                del unpacked[:grouping]
            else:
                setattr(self, name, unpacked.pop(0))

    def prettify(self, prefix:str='') -> str:
        rows: list[tuple[str, str]] = []
        for name, _ in self._metadata.fields:
            value = getattr(self, name)
            rows.append((name, value))
        
        widest_name = len(max(rows, key=lambda row: len(row[0]))[0])
        
        return '\n'.join(f'{prefix}{name:<{widest_name}}  {value!r}' for name, value in rows)

    _metadata: StructureMetadata

    def __init_subclass__(cls):
        cls._metadata = StructureMetadata()
        meta = cls._metadata

        for name, annotation in cls.__annotations__.items():
            origin, args = typing.get_origin(annotation), typing.get_args(annotation)
            value = getattr(cls, name, None)
            if issubclass(annotation, StructuredField):
                meta.fields.append((name, 1))
                meta.size += annotation.size
                meta.format += annotation.format
            elif origin == list and len(args) == 1 and issubclass(args[0], StructuredField) and isinstance(value, int):
                meta.fields.append((name, value))
                meta.size += args[0].size * value
                meta.format += f'{value}{args[0].format}'
            elif annotation == bytes and isinstance(value, int):
                meta.fields.append((name, 1))
                meta.size += value
                meta.format += f'{value}s'
            else:
                raise ValueError(f'`{annotation!r}` is not a valid binary.structure field.')

class BYTE(int, StructuredField):
    size: int = 1
    format: str = 'B'

class CHAR(bytes, StructuredField):
    size: int = 1
    format: str = 'c'

class WORD(int, StructuredField):
    size: int = 2
    format: str = 'H'

class LONG(int, StructuredField):
    size: int = 4
    format: str = 'l'

class DWORD(int, StructuredField):
    size: int = 4
    format: str = 'L'

def ARRAY(length: int) -> typing.Any:
    return length

def STRING(length: int) -> typing.Any:
    return length

if __name__ == "__main__":
    import doctest
    doctest.testmod()
