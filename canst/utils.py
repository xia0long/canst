import os
import random

import cantools

from .can import Frame
from .constants import *


def frame_data_to_str(data: list) -> str:
    """Convert frame data from list to string."""
    return "".join("{0:02x}".format(i) for i in data)


def frame_id_to_str(arb_id: int) -> str:
    """Convert frame arb id to string."""
    return str(hex(arb_id))[2:]


def str_to_frame_data(s) -> list:
    """Convert string to frame data."""
    return [int(s[i : i + 2], 16) for i in range(0, len(s), 2)]


def str_to_frame(s: str) -> Frame:
    """Convert can message format from string to frame."""
    s = s.strip().split(" ")[-1]
    arb_id_str, data_str = s.strip().split("#")
    arb_id = int(arb_id_str, 16)
    data = str_to_frame_data(data_str)
    return Frame(arb_id=arb_id, data=data)


def frame_to_str(frame: Frame) -> str:
    """Convert can data from str to ascii.
    use '.' to replace the byte can't be print."""
    return "".join(chr(b) if (b >= 0x20 and b <= 0x7E) else "." for b in frame.data)


def parse_arb_id(arb_id: int):
    """Return IDH and IDL."""
    return divmod(arb_id, 0x100)


def generate_random_arb_id(
    min_arb_id: int = MIN_ARB_ID, max_arb_id: int = MAX_ARB_ID
) -> int:
    """Get random arb_id."""
    arb_id = random.randint(min_arb_id, max_arb_id)
    return arb_id


def generate_random_data(
    min_data_len: int = MIN_DATA_LEN, max_data_len: int = MAX_DATA_LEN
) -> str:
    """Get random frame data."""
    data_len = random.randint(min_data_len, max_data_len)
    data = [random.randint(MIN_BYTE, MAX_BYTE) for i in range(data_len)]
    return data


def dbc_to_dict(file_path):
    """Convert dbc file to a dict."""
    D = {}
    db = cantools.db.load_file(file_path)
    for message in db.messages:
        D[message.frame_id] = {
            "id": hex(message.frame_id),
            "name": message.name,
            "length": message.length,
            "cycle_time": message.cycle_time,
            "is_extended_frame": message.is_extended_frame,
            "signals": {},
        }

        for signal in message.signals:
            D[message.frame_id]["signals"][signal.name] = {
                "name": signal.name,
                "unit": signal.unit,
                "start": signal.start,
                "length": signal.length,
                "factor": signal.scale,
                "offset": signal.offset,
                "maximum": signal.maximum,
                "minimum": signal.minimum,
                "is_big_endian": False
                if signal.byte_order == "little_endian"
                else True,
            }

    return D
