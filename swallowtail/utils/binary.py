from multiprocessing.sharedctypes import Value
import typing
import dataclasses
import struct
import math

class StructuredField:
    size: int
    format: str

@dataclasses.dataclass
class StructuredFieldMetadata:
    name: str = ''
    size: int = -1
    format: str = ''
    structure: typing.Optional[typing.Type['Structure']] = None
    type_cast: typing.Optional[type] = None
    array_length: typing.Optional[int] = None

    def pull_from_unpacked(self, unpacked: list[typing.Any]) -> typing.Any:
        if self.array_length is not None:
            if self.structure is not None:
                return [self.structure(unpacked.pop(0)) for _ in range(self.array_length)]
            else:
                result = unpacked[:self.array_length]
                del unpacked[:self.array_length]
                return [self.type_cast(x) for x in result] if self.type_cast is not None else result
        elif self.structure is not None:
            return self.structure(unpacked.pop(0))
        else:
            return self.type_cast(unpacked.pop(0)) if self.type_cast is not None else unpacked.pop(0)
    
    def invalid_reason(self) -> str | None:
        if not self.name: return 'fields must have names'
        if self.array_length is not None and self.array_length <= 0: return 'cannot have an array length of 0'
        if self.size <= 0: return 'cannot have a size of 0 (make sure your fields are annotated)'
        if len(self.format) <= 0: return 'format resolved to empty string'
        if self.structure is not None and not issubclass(self.structure, Structure): return f'invalid field type {self.structure!r}'
        if self.structure is not None and self.type_cast is not None and self.type_cast != self.structure: return 'conflicting type_cast and structure'
        return None

    def valid(self) -> bool:
        return self.invalid_reason() is None

@dataclasses.dataclass
class StructureMetadata:
    size: int = 0
    format: str = ''
    fields: list[StructuredFieldMetadata] = dataclasses.field(default_factory=list) # pls don't modify directly

    def add_field(self, field: StructuredFieldMetadata) -> None:
        self.fields.append(field)
        self.size += field.size
        self.format += field.format

class BYTE(int, StructuredField):
    size: int = 1
    format: str = 'B'

class CHAR(bytes, StructuredField):
    size: int = 1
    format: str = 'c'

    def __repr__(self):
        try:
            return repr(self.decode())
        except:
            return super().__repr__()

class STRING(bytes): # notice it does not inherit from StructuredField since it's hardcoded
    def __repr__(self):
        try:
            human_readable = self.rstrip(b'\x00').decode()
            if not human_readable or not human_readable.isprintable():
                raise ValueError
            else:
                return repr(human_readable)
        except:
            return super().__repr__()

class WORD(int, StructuredField):
    size: int = 2
    format: str = 'H'

    def __repr__(self):
        return f'{self:0{self.size * 2}x}h ({self:d})'

class LONG(int, StructuredField):
    size: int = 4
    format: str = 'l'

class DWORD(int, StructuredField):
    size: int = 4
    format: str = 'L'

    def __repr__(self):
        return f'{self:0{self.size * 2}x}h ({self:,d})'

def LENGTH(length: int) -> typing.Any:
    return length

class Structure:
    '''
    >>> class Test(Structure):
    ...     x: BYTE
    ...     y: CHAR
    ...     z: DWORD
    ...     w: list[CHAR] = LENGTH(3)
    ...     p: STRING = LENGTH(11)
    ...
    >>> Test._metadata.size
    20
    >>> Test._metadata.format
    'BcL3c11s'
    >>> Test(b'x')
    Traceback (most recent call last):
    ...
    ValueError: This structure requires exactly 20 bytes, but you provided 1.
    >>> t = Test(b'\\xFFH\\x05\\x00\\x00\\x00ABCHELLO WORLD')
    >>> t.x, t.y, t.z, t.w, t.p
    (255, 'H', 0x5, ['A', 'B', 'C'], 'HELLO WORLD')
    '''
    _metadata: StructureMetadata

    def __init__(self, data: bytes):
        if self._metadata.size != len(data):
            raise ValueError(f'This structure requires exactly {self._metadata.size} bytes, but you provided {len(data)}.')
        
        unpacked = list(struct.unpack(f'<{self._metadata.format}', data))
        for field in self._metadata.fields:
            setattr(self, field.name, field.pull_from_unpacked(unpacked))

    def __init_subclass__(cls):
        cls._metadata = StructureMetadata()
        meta = cls._metadata

        for name, annotation in cls.__annotations__.items():
            origin, args = typing.get_origin(annotation), typing.get_args(annotation)
            value = getattr(cls, name, None)
            field = StructuredFieldMetadata(name=name)

            if issubclass(annotation, StructuredField):
                field.size = annotation.size
                field.format = annotation.format
                field.type_cast = annotation
            elif issubclass(annotation, Structure):
                field.size = annotation._metadata.size
                field.format = f'{field.size}s'
                field.structure = annotation
            elif origin == list and len(args) == 1:
                array_element_type = args[0]
                field.array_length = value

                if issubclass(array_element_type, Structure):
                    field.structure = array_element_type
                    field.size = field.array_length * array_element_type._metadata.size
                    field.format = f'{array_element_type._metadata.size}s' * field.array_length
                elif issubclass(array_element_type, StructuredField):
                    field.size = field.array_length * array_element_type.size
                    field.format = f'{field.array_length}{array_element_type.format}'
                    field.type_cast = array_element_type
            elif annotation == STRING and isinstance(value, int):
                string_length = value
                field.size = string_length
                field.format = f'{string_length}s'
                field.type_cast = STRING
            
            if not field.valid():
                raise ValueError(f'`{annotation!r}` is not a valid binary.Structure field. Error: {field.invalid_reason()}')

            meta.add_field(field)

    def prettify(self, prefix:str='') -> str:
        widest_field = max(self._metadata.fields, key=lambda field: len(field.name))
        left_column_width = len(widest_field.name)
        
        rows: list[str] = []
        for field in self._metadata.fields:
            value = getattr(self, field.name)
            if field.structure is not None:
                if field.array_length is not None:
                    rows.append(
                        f"{prefix}{field.name:<{left_column_width}}  {field.structure.__name__}[{field.array_length}]"
                    )
                    index_width = math.ceil(math.log10(field.array_length - 1))
                    for i, v in enumerate(value):
                        rows.append(
                            f"{prefix}{' ' * left_column_width}  {'[' + str(i) + ']':<{index_width + 2}} {v.prettify(prefix=prefix + ' ' * (left_column_width + index_width + 5)).lstrip()}"
                        )
                else:
                    rows.append(
                        f"{prefix}{field.name:<{left_column_width}}  {field.structure.__name__}\n{value.prettify(prefix=prefix + ' ' * (left_column_width + 2) + '    ')}"
                    )
            else:
                rows.append(
                    f'{prefix}{field.name:<{left_column_width}}  {value!r}' 
                )

        return '\n'.join(rows)
    
    def __repr__(self) -> str:
        field_list = ', '.join(f'{field.name}=`{getattr(self, field.name)!r}`' for field in self._metadata.fields[:3])
        return f"<{self.__class__.__name__} {field_list}{' ...' if len(self._metadata.fields) > 3 else ''}>"

StructureSubclass = typing.TypeVar('StructureSubclass', bound=Structure)
# ^ used to generically refer to a subclass of Structure
# for example:
'''
def function_that_builds_a_structure(structure: typing.Type[StructureSubclass]) -> StructureSubclass:
    return structure(b'blah')
'''

if __name__ == "__main__":
    import doctest
    doctest.testmod()
