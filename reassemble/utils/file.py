from os import PathLike
from pathlib import Path
from io import BytesIO, BufferedReader, BufferedWriter

Readable = str | Path | PathLike | BytesIO | bytes | BufferedReader
Writable = str | Path | PathLike | BytesIO | BufferedWriter

def read(readable: Readable) -> bytes:
    if isinstance(readable, bytes):
        return readable
    elif isinstance(readable, (BytesIO, BufferedReader)):
        return readable.read()
    else:
        with open(readable, 'rb') as file_handle:
            return file_handle.read()

def write(writable: Writable, data: bytes) -> None:
    if isinstance(writable, (BytesIO, BufferedWriter)):
        writable.write(data)
    else:
        with open(writable, 'wb') as file_handle:
            file_handle.write(data)
