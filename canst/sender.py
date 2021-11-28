import time
from multiprocessing import Process

from .can import Frame
from .constants import DELAY
from .utils import *


def get_frame_from_file(
    file_path: str = None,
    start_line: int = None,
    end_line: int = None,
) -> Frame:

    with open(file_path, "r") as f:
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

            frame = str_to_frame(line.split(" ")[-1])
            yield frame


def send(
    dev,
    messages: list,
    delays: list,
    file_path: str = None,
    start_line: int = None,
    end_line: int = None,
    arb_id_filter: str = None,
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
                _send_process.join()

        elif messages and not delays:
            for message in messages:
                dev.send(str_to_frame(message))

        elif file_path:

            frames = get_frame_from_file(
                file_path,
                start_line=start_line,
                end_line=end_line,
                arb_id_filter=arb_id_filter,
            )
            while True:
                for frame in frames:
                    dev.send(frame)
                    time.sleep(DELAY)
                if not loop:
                    break
        else:
            print("Wrong args.")

    except KeyboardInterrupt:
        _send_process.terminate()
        print("\nSend canceled.")
