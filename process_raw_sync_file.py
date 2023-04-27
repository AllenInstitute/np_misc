"""
Process a raw .sync file + timestamps.txt file into a .h5 file.

Useful for experiments where automatic conversion post-experiment was
interrupted.

- requires the `sync` and `mpeconfig` packages from AIBS-MPE
"""
from __future__ import annotations

from datetime import datetime
from hashlib import md5
from pathlib import Path
from typing import Optional

try:
    from sync.ni.DIU32 import DigitalInputU32
except NotImplementedError:
    print(
        '\nWARNING: NI-DAQmx is not installed.\n',
        'Processing the sync file doesn\'t require NI-DAQmx, but PyDAQmx components are imported in `sync.sync_controller`, which we need.',
        'As a temporary fix, just comment out L45 in `sync_controller.py`:\n\tfrom .ni.DIU32 import DigitalInputU32',
        'and rerun this processing script.',
        sep='\n')
import mpetk.mpeconfig as mpeconfig

from sync.datasets import RecordingData
from sync.sync_controller import Sync


def process_raw_sync_file(
    raw_sync_file: str | Path,
    rig_id: str,
    timestamps_file: Optional[str | Path] = None,
    comp_id: Optional[str] = None,
    ) -> Path:
    """Process a raw .sync file + timestamps.txt file into a .h5 file.

    Useful for experiments where automatic conversion post-experiment was
    interrupted.
    
    - rig_id: for getting config
            - AIBS rig ID, for look-up in mpe-computers/
            - e.g. 'NP.1'
    - comp_id: [optional] for getting config, if rig config isn't specific enough
            - hostname of the computer that sync was recorded on
            - e.g. 'w10dtsm18306'
    - timestamps_file: [optional] path to `*_timestamps.txt` file
    """

    raw_sync_file = Path(raw_sync_file)
    
    
    if timestamps_file is None:
        timestamps_file = raw_sync_file.parent / (raw_sync_file.stem + '_timestamps.txt')
    timestamps_file = Path(timestamps_file)
       
       
    config: dict | None = mpeconfig.source_configuration('sync', rig_id=rig_id, comp_id=comp_id or '')
    if config is None:
        raise ValueError(f'No config found for rig_id {rig_id}')
    # reconstruct some config values for the recording:
    config['output_dir'] = raw_sync_file.parent
    config['output_filename'] = raw_sync_file.name


    recording_data = RecordingData(config)
    # reconstruct some parameters for the recording:
    recording_data.output_file = str(raw_sync_file)
    recording_data.time_file = str(timestamps_file)
    # get required timestamps:
    with open(recording_data.time_file, 'r') as f:
        timestamps = f.readlines()
    recording_data.timestamp = datetime.fromisoformat(str(timestamps[0]).strip())
    recording_data.stop_time = datetime.fromisoformat(str(timestamps[-1]).strip())
    recording_data.samples_recorded = len(timestamps) * recording_data.buffer_size
    # this id is only used for logging - doesn't need to match the original
    # (which isn't saved anywhere). Using original format for consistency:
    recording_data.recording_id = md5(str(datetime.now()).encode()).hexdigest()[:7]


    sync = Sync(config)
    sync.recording_data = recording_data


    print(
        'Processing raw data. The output .h5 file will be saved to the raw .sync file\'s directory.',
        '\nThis will take a while...'
        )


    processed_h5_file = sync.process_raw_data()
    return Path(processed_h5_file)
