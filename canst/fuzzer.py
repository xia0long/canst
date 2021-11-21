import time
import random

from .can import Frame
from .constants import *
from .utils import *


def random_fuzz(
    dev,
    arb_id_filter: str = None,
    min_arb_id: str = hex(MIN_ARB_ID)[2:],
    max_arb_id: str = hex(MAX_ARB_ID)[2:],
    min_data_len: int = MIN_DATA_LEN,
    max_data_len: int = MAX_DATA_LEN,
    delay: float = DELAY,
) -> None:
    """Send random message."""
    print("Send random messages, press 'control+c' to exit.")
    if arb_id_filter:
        try:
            arb_id_list = [
                int(i.strip(), 16) for i in arb_id_filter.split(" ") if i is not None
            ]
        except Exception as e:
            raise ValueError("The arb_id_filter you input is invalid.")
            print(e)
    try:
        while True:
            if arb_id_filter:
                arb_id = random.choice(arb_id_list)
            else:
                arb_id = generate_random_arb_id(
                    int(min_arb_id, 16), int(max_arb_id, 16)
                )
            data = generate_random_data(min_data_len, max_data_len)
            dev.send(Frame(arb_id=arb_id, data=data))
            time.sleep(delay)
    except KeyboardInterrupt:
        print("\nSend canceled.")


def mutate_fuzz(dev, message: str, delay: float = DELAY) -> None:
    """Mutate fuzz."""
    print(f"Send mutated messages(based on {message}), press 'control+c' to exit.")
    init_arb_id, init_data = message.split("#")

    def arb_id_generator(arb_id):
        while "." in arb_id:
            if arb_id[0] == ".":
                arb_id = arb_id.replace(".", random.choice("01234567"), 1)
            else:
                arb_id = arb_id.replace(".", random.choice("0123456789abcdef"), 1)
        else:
            return int(arb_id, 16)

    def data_generator(data):
        while "." in data:
            data = data.replace(".", random.choice("0123456789abcdef"), 1)
        return str_to_frame_data(data)

    try:
        while True:
            frame = Frame(
                arb_id=arb_id_generator(init_arb_id), data=data_generator(init_data)
            )
            dev.send(frame)
            time.sleep(delay)
    except KeyboardInterrupt:
        print("\nSend canceled.")
