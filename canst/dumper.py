import os

from .utils import *


def dump(
    dev, arb_id_filter: str = None, data_filter: str = None, log_path: str = None
) -> None:
    """Dump canbus message."""
    print("Dumping CAN traffic, press 'ctrl+c' to exit.")
    if log_path:
        f = open(log_path, "w+")

    try:
        while True:
            frame = dev.recv()
            if not frame:
                continue
            frame_id = hex(frame.arb_id)[2:]
            frame_data_str = frame_data_to_str(frame.data)

            # arb_id filter
            if arb_id_filter:
                arb_id_filter_list = [
                    arb_id.strip()
                    for arb_id in arb_id_filter.split(" ")
                    if arb_id is not None
                ]
                if str(frame_id) not in arb_id_filter_list:
                    continue

            # data filter
            if data_filter:
                data_filter_list = [
                    data.strip() for data in data_filter.split(" ") if data is not None
                ]

                if not any(data in frame_data_str for data in data_filter_list):
                    continue

            frame_info = "({:.5f}) {} {}#{}".format(
                # time.time(),
                frame.timestamp,  # start from zero
                dev.ndev,
                frame_id,
                frame_data_to_str(frame.data),
            )

            # print to terminal
            print(frame_info)

            # write to file
            if log_path:
                f.write(frame_info + "\n")

    except KeyboardInterrupt:
        print("\nDump canceled.")

    finally:
        if log_path:
            f.close()
