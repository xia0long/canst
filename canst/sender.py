import time

from .can import Frame
from .constants import DELAY
from .utils import *


def get_frame_from_file(
    file_path: str = None,
    start_line: int = None,
    end_line: int = None,
    arb_id_filter=None,
) -> Frame:

    if arb_id_filter:
        arb_id_filter = [arb_id for arb_id in arb_id_filter.split(",")]

    f = open(file_path, "r")
    current_line_index = 0
    for line in f.readlines():
        if not line:
            continue

        # Skip the lines before the start line
        if start_line and current_line_index < start_line:
            current_line_index += 1
            continue

        # Skip the lines after the end line
        if end_line and current_line_index > end_line:
            break

        # Skip the lines that don't match the filter
        if arb_id_filter:
            arb_id = int(line.split(" ")[0])
            if arb_id not in arb_id_filter:
                current_line_index += 1
                continue

        frame = str_to_frame(line.split(" ")[-1])
        yield frame


def send(
    dev,
    message: str,
    file_path: str = None,
    start_line: int = None,
    end_line: int = None,
    arb_id_filter: str = None,
    delay: float = DELAY,
    loop: bool = False,
) -> None:

    try:
        while True:
            if message:
                dev.send(str_to_frame(message))
                time.sleep(delay)

            if file_path:
                frames = get_frame_from_file(
                    file_path,
                    start_line=start_line,
                    end_line=end_line,
                    arb_id_filter=arb_id_filter,
                )
                for frame in frames:
                    dev.send(frame)
                    time.sleep(delay)
            if not loop:
                break

    except KeyboardInterrupt:
        print("\nSend canceled.")
