from .. import utils

class BaseParser:
    def __init__(self, file: utils.file.Readable):
        raise NotImplementedError
    
    def prettify(self) -> str:
        '''
        Returns a human readable string containing metadata about the data being parsed.
        '''
        raise NotImplementedError
