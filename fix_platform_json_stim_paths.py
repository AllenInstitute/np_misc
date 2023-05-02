"""Remove instances of  '//W10DT713843/W10DT713842/C/ProgramData/AIBS_MPE/MVR/data'"""
from __future__ import annotations


import doctest
import json
import pathlib
import tempfile
import os
from typing import Any

import np_config
import np_session

KEY = 'script_name'

def fix_platform_json(path: pathlib.Path) -> None:
    """
    >>> d = {"script_name": "//W10DT713843/W10DT713842/C/ProgramData/AIBS_MPE/MVR/data"}
    >>> with tempfile.NamedTemporaryFile(mode='w', delete=True) as f:
    ...     p = pathlib.Path(f.name)
    ...     _ = p.write_bytes(json.dumps(d, indent=4).encode())
    ...     fix_platform_json(p)
    ...     json.loads(p.read_bytes())[KEY]
    '//W10DT713843/C/ProgramData/AIBS_MPE/MVR/data'
    """
    path = pathlib.Path(path)
    json_contents = json.loads(path.read_bytes())
    if KEY in json_contents:
        new_path = remove_second_host(json_contents[KEY])
        if new_path != json_contents[KEY]:
            json_contents = replace_stim_path(json_contents, new_path)
            _ = path.write_bytes(json.dumps(json_contents, indent=4).encode())
        else:
            print(f'No change needed for {json_contents[KEY]}')
    else:
        print(f'No key {KEY} in {path}')


def replace_stim_path(json_contents: dict[str, Any], new_path: str | pathlib.Path) -> dict[str, Any]:
    """
    >>> replace_stim_path({KEY: '//W10DT713843/W10DT713842/C/ProgramData/AIBS_MPE/MVR/data'}, '//W10DT713843/C/ProgramData/AIBS_MPE/MVR/data')
    {'script_name': '//W10DT713843/C/ProgramData/AIBS_MPE/MVR/data'}
    """
    return json_contents | {KEY: np_config.normalize_path(new_path)}
    
    
def remove_second_host(path: str | pathlib.Path) -> pathlib.Path:
    """
    Assumes there is a drive letter (e.g. C:\ Win) after one or more hosts. 

    >>> remove_second_host('//W10DT713843/W10DT713842/C/ProgramData/AIBS_MPE/MVR/data').as_posix()
    '//W10DT713843/C/ProgramData/AIBS_MPE/MVR/data'
    >>> remove_second_host('C:/ProgramData/AIBS_MPE/MVR/data').as_posix()
    'C:/ProgramData/AIBS_MPE/MVR/data'
    >>> remove_second_host('/W10DT713843/W10DT713842/C/ProgramData/AIBS_MPE/MVR/data').as_posix()
    '/W10DT713843/C/ProgramData/AIBS_MPE/MVR/data'
    """
    path = pathlib.Path(path)
    parts = tuple(_ for _ in str(path).split(os.sep) if _)
    for idx, p in enumerate(parts):
        if len(p) == 1:
            break
    else:
        return path
    
    return pathlib.Path(path.root, parts[0], *parts[idx:])


def main() -> None:
    for s in np_session.sessions():
        fix_platform_json(s.platform_json.path)


if __name__ == "__main__":
    doctest.testmod(verbose=True, report=True, raise_on_error=True)
    main()