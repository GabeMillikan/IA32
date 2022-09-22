# This file exists purely as a proxy to the `../swallowtail` module.
# Without this file, it wouldn't be possible to do `import swallowtail` from the `./examples/` directory.

import sys, pathlib, importlib.util

examples_folder = pathlib.Path(__file__).parent
repository_folder = examples_folder.parent
library_entry_point = repository_folder / 'swallowtail' / '__init__.py'

swallowtail_spec = importlib.util.spec_from_file_location('swallowtail', str(library_entry_point.absolute()))
if swallowtail_spec is None or swallowtail_spec.loader is None:
    raise ImportError('Failed to import swallowtail. Make sure to directly run the example files, rather than importing them.')

swallowtail = importlib.util.module_from_spec(swallowtail_spec)
sys.modules['swallowtail'] = swallowtail
swallowtail_spec.loader.exec_module(swallowtail)
