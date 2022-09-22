from inspect import signature
from msilib.schema import Signature
from multiprocessing.sharedctypes import Value
import typing

from .. import utils
from ..utils import binary
from .base_parser import BaseParser

class IMAGE_DOS_HEADER32(binary.Structure):
    e_magic: binary.WORD                          # Magic number
    e_cblp: binary.WORD                           # Bytes on last page of file
    e_cp: binary.WORD                             # Pages in file
    e_crlc: binary.WORD                           # Relocations
    e_cparhdr: binary.WORD                        # Size of header in paragraphs
    e_minalloc: binary.WORD                       # Minimum extra paragraphs needed
    e_maxalloc: binary.WORD                       # Maximum extra paragraphs needed
    e_ss: binary.WORD                             # Initial (relative) SS value
    e_sp: binary.WORD                             # Initial SP value
    e_csum: binary.WORD                           # Checksum
    e_ip: binary.WORD                             # Initial IP value
    e_cs: binary.WORD                             # Initial (relative) CS value
    e_lfarlc: binary.WORD                         # File address of relocation table
    e_ovno: binary.WORD                           # Overlay number
    e_res: list[binary.WORD] = binary.LENGTH(4)   # Reserved words
    e_oemid: binary.WORD                          # OEM identifier (for e_oeminfo)
    e_oeminfo: binary.WORD                        # OEM information: binary.WORD e_oemid specific
    e_res2: list[binary.WORD] = binary.LENGTH(10) # Reserved words
    e_lfanew: binary.LONG                         # File address of new exe header

IMAGE_FILE_MACHINE_I386 = 0x014C # x86
IMAGE_FILE_MACHINE_IA64 = 0x0200 # Intel Itanium
IMAGE_FILE_MACHINE_AMD64 = 0x8664 # AMD64
class IMAGE_FILE_HEADER(binary.Structure):
    machine: binary.WORD                   # see IMAGE_FILE_MACHINE_* constants above
    number_of_sections: binary.WORD        # how many IMAGE_SECTION_HEADER's and subsequent sections are there
    time_date_stamp: binary.DWORD
    pointer_to_symbol_table: binary.DWORD
    number_of_symbols: binary.DWORD
    size_of_optional_header: binary.WORD
    characteristics: binary.WORD

class IMAGE_DATA_DIRECTORY(binary.Structure):
    virtual_address: binary.DWORD
    size: binary.DWORD

IMAGE_NUMBEROF_DIRECTORY_ENTRIES = 16
class IMAGE_OPTIONAL_HEADER32(binary.Structure):
    # Standard Fields
    magic: binary.WORD
    major_linker_version: binary.BYTE
    minor_linker_version: binary.BYTE
    size_of_code: binary.DWORD
    size_of_initialized_data: binary.DWORD
    size_of_uninitialized_data: binary.DWORD
    address_of_entry_point: binary.DWORD
    base_of_code: binary.DWORD
    base_of_data: binary.DWORD

    # NT additional fields
    image_base: binary.DWORD
    section_alignment: binary.DWORD
    file_alignment: binary.DWORD
    major_operating_system_version: binary.WORD
    minor_operating_system_version: binary.WORD
    major_image_version: binary.WORD
    minor_image_version: binary.WORD 
    major_subsystem_version: binary.WORD
    minor_subsystem_version: binary.WORD
    win32_version_value: binary.DWORD
    size_of_image: binary.DWORD
    size_of_headers: binary.DWORD
    check_sum: binary.DWORD
    subsystem: binary.WORD
    dll_characteristics: binary.WORD
    size_of_stack_reserve: binary.DWORD
    size_of_stack_commit: binary.DWORD
    size_of_heap_reserve: binary.DWORD
    size_of_heap_commit: binary.DWORD
    loader_flags: binary.DWORD
    number_of_rva_and_sizes: binary.DWORD
    data_directory: list[IMAGE_DATA_DIRECTORY] = binary.LENGTH(IMAGE_NUMBEROF_DIRECTORY_ENTRIES)

class IMAGE_NT_HEADERS32(binary.Structure):
    signature: binary.DWORD
    file_header: IMAGE_FILE_HEADER
    optional_header: IMAGE_OPTIONAL_HEADER32

IMAGE_SIZEOF_SHORT_NAME = 8
class IMAGE_SECTION_HEADER(binary.Structure):
    name: binary.STRING = binary.LENGTH(IMAGE_SIZEOF_SHORT_NAME)
    physical_address_or_virtual_size: binary.DWORD # in C, this is a union
    virtual_address: binary.DWORD
    size_of_raw_data: binary.DWORD
    pointer_to_raw_data: binary.DWORD
    pointer_to_relocations: binary.DWORD
    pointer_to_linenumbers: binary.DWORD
    number_of_relocations: binary.WORD
    number_of_linenumbers: binary.WORD
    characteristics: binary.DWORD

class WindowsPortableExecutable(BaseParser):
    raw_file_data: bytes
    image_dos_header: IMAGE_DOS_HEADER32
    image_nt_header: IMAGE_NT_HEADERS32
    image_section_headers: list[IMAGE_SECTION_HEADER]

    def __init__(self, file: utils.file.Readable):
        self.raw_file_data = utils.file.read(file)

        self.image_dos_header = self.read_struct_at_offset(IMAGE_DOS_HEADER32, 0)
        if self.image_dos_header.e_magic != 0x5A4D:
            raise ValueError('The provided binary is not a WindowsPortableExecutable. `e_magic` mismatch.')

        self.image_nt_header = self.read_struct_at_offset(IMAGE_NT_HEADERS32, self.image_dos_header.e_lfanew)
        if self.image_nt_header.file_header.machine != IMAGE_FILE_MACHINE_I386:
            raise ValueError('Only x86 executables are supported at the moment.')

        # image section headers occur directly after image_nt_header
        self.image_section_headers = []
        for i in range(self.image_nt_header.file_header.number_of_sections):
            self.image_section_headers.append(
                self.read_struct_at_offset(
                    IMAGE_SECTION_HEADER,
                    self.image_dos_header.e_lfanew + IMAGE_NT_HEADERS32._metadata.size + i * IMAGE_SECTION_HEADER._metadata.size
                )
            )
    
    def read_struct_at_offset(self, structure: typing.Type[binary.StructureSubclass], offset: int) -> binary.StructureSubclass:
        return structure(self.raw_file_data[offset:offset+structure._metadata.size])

    def prettify(self) -> str:
        return \
            f"IMAGE_DOS_HEADER\n" \
            f"{self.image_dos_header.prettify(prefix='    ')}" \
            f'\n\n' \
            f"IMAGE_FILE_HEADER\n" \
            f"{self.image_nt_header.prettify(prefix='    ')}" \
            f'\n\n' \
            f'IMAGE_SECTION_HEADERS[{len(self.image_section_headers)}]\n    ' \
            + f'\n    '.join(repr(x) for x in self.image_section_headers)
