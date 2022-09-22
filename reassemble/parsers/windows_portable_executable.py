import utils.file

class WindowsPortableExecutable:
    raw_file_data: bytes

    def __init__(self, file: utils.file.Readable):
        self.raw_file_data = utils.file.read(file)

        # TODO: actually parse stuff
