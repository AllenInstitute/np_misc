"""Remove instances of  '//W10DT713843/W10DT713842/C/ProgramData/AIBS_MPE/MVR/data'"""
from __future__ import annotations


import doctest
import json
import pathlib
import tempfile

import np_config
import np_session

def replace_path_in_platform_json(json: pathlib.Path, new_path: pathlib.Path):
    """
    >>> with tempfile.mkstemp() as f:
        pathlib.Path(f).
    """
def remove_second_host(path: str | pathlib.Path) -> pathlib.Path:
    """
    Assumes there is a drive letter (e.g. C:\ Win) after one or more hosts. 

    >>> remove_second_host('//W10DT713843/W10DT713842/C/ProgramData/AIBS_MPE/MVR/data')
    '//W10DT713843/C/ProgramData/AIBS_MPE/MVR/data'
    """
    path = pathlib.Path(path)
    for idx, p in enumerate(path.parts):
        if len(p) == 1:
            break
    else:
        return path
    return pathlib.Path(path.parts[0], path.parts[idx:])

if __name__ == "__main__":
    doctest.testmod(raise_on_error=True)
    main()