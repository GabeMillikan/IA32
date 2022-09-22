import typing

from .. import utils
from ..utils import binary
from .base_parser import BaseParser

class IMAGE_DOS_HEADER32(binary.Structure):
    e_magic: binary.WORD                         # Magic number
    e_cblp: binary.WORD                          # Bytes on last page of file
    e_cp: binary.WORD                            # Pages in file
    e_crlc: binary.WORD                          # Relocations
    e_cparhdr: binary.WORD                       # Size of header in paragraphs
    e_minalloc: binary.WORD                      # Minimum extra paragraphs needed
    e_maxalloc: binary.WORD                      # Maximum extra paragraphs needed
    e_ss: binary.WORD                            # Initial (relative) SS value
    e_sp: binary.WORD                            # Initial SP value
    e_csum: binary.WORD                          # Checksum
    e_ip: binary.WORD                            # Initial IP value
    e_cs: binary.WORD                            # Initial (relative) CS value
    e_lfarlc: binary.WORD                        # File address of relocation table
    e_ovno: binary.WORD                          # Overlay number
    e_res: list[binary.WORD] = binary.ARRAY(4)   # Reserved words
    e_oemid: binary.WORD                         # OEM identifier (for e_oeminfo)
    e_oeminfo: binary.WORD                       # OEM information: binary.WORD e_oemid specific
    e_res2: list[binary.WORD] = binary.ARRAY(10) # Reserved words
    e_lfanew: binary.LONG                        # File address of new exe header


class WindowsPortableExecutable(BaseParser):
    raw_file_data: bytes

    def __init__(self, file: utils.file.Readable):
        self.raw_file_data = utils.file.read(file)

        self.image_dos_header = self.read_struct_at_offset(IMAGE_DOS_HEADER32, 0)
    
    def read_struct_at_offset(self, structure: typing.Type[binary.Structure], offset: int):
        return structure(self.raw_file_data[offset:structure._metadata.size])

    def prettify(self) -> str:
        return \
            f"IMAGE_DOS_HEADER\n" \
            f"{self.image_dos_header.prettify(prefix='  - ')}"
