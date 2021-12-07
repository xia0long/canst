import time
from multiprocessing import Process

from .can import Frame
from .constants import DELAY
from .utils import *


def parse_line(line):
    """
    line format: (timestamp) canX arb_id#data
    e.g. (1638179661.354936) can0 0CF00400#F07D86401FFFFFFF
    """
    part1, part2, part3 = line.split(" ")
    return {
        "timestamp": float(part1.strip("(").rstrip(")")),
        "dev": part2,
        "frame_str": part3,
    }


def get_frame_list_from_file(
    file_path: str = None,
    start_line: int = None,
    end_line: int = None,
) -> list:

    frame_list = []
    with open(file_path, "r") as f:
        index = 0
        data = f.readlines()
        for index, line in enumerate(data[:-1]):
            # Skip the lines before the start line
            if start_line is not None and index < start_line:
                index += 1
                continue

            # Skip the lines after the end line
            elif end_line is not None and index > end_line:
                break

            if index == total_lines - 2:  # the last line
                delay = 0
            else:
                next_line = data[index + 1]
                delay = (
                    parse_line(next_line)["timestamp"] - parse_line(line)["timestamp"]
                )
            frame = str_to_frame(parse_line(line)["frame_str"])
            frame_list.append((frame, delay))

    return frame_list


def send(
    dev,
    messages: list,
    delays: list,
    file_path: str = None,
    start_line: int = None,
    end_line: int = None,
    loop: bool = False,
) -> None:
    def _send(message, delay):
        while True:
            dev.send(str_to_frame(message))
            time.sleep(delay)

    try:
        if messages and delays:
            assert len(messages) == len(
                delays
            ), "The quantity of message and delay need to be the same."
            for message, delay in zip(messages, delays):
                _send_process = Process(target=_send, args=[message, delay])
                _send_process.start()

        elif messages and not delays:
            for message in messages:
                dev.send(str_to_frame(message))

        elif file_path:
            data = get_frame_list_from_file(
                file_path,
                start_line=start_line,
                end_line=end_line,
            )
            while True:
                for frame, delay in data:
                    dev.send(frame)
                    time.sleep(delay)
                if not loop:
                    break
        else:
            print("Wrong args.")

    except KeyboardInterrupt:
        print("\nSend canceled.")
