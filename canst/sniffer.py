import time
import struct
import curses
import binascii
from multiprocessing import Process, Manager

from .utils import *

T = Manager().dict()

def parse_frame(data: Frame.data, signals: dict) -> dict:
    message = {}
    b = "".join("{0:08b}".format(i) for i in data)
    for name, signal in signals.items():
        v = b[signal["start"]: signal["start"] + signal["length"]]
        v = int(v, 2)
        if not signal["is_big_endian"] and v > 255:
            v = hex(v)[2:]
            v = bytearray.fromhex(v)
            v.reverse()
            v = int(v.hex(), 16)
        v = signal["offset"] + signal["factor"] * v

        message[name] = {
            "value": v,
            "unit": signal["unit"] if signal["unit"] is not None else ""
        }

    return message


def parse_data(data, mode):
    if mode:
        data_str = " ".join("{0:08b}".format(i) for i in data)
    else:
        data_str = " ".join("{0:02x}".format(i) for i in data)

    return data_str


def update_t(start_time, T):
    """Save frames within 5 second to T."""
    for arb_id, frame_list in T.items():
        for index, frame in enumerate(frame_list):
            if time.time() - start_time - frame.timestamp > 5:
                frame_list.pop(index)
                T[arb_id] = frame_list
            else:
                break


def traffic_handler(dev, T):
    start_time = time.time()
    while True:
        frame = dev.recv()
        if not frame:
            update_t(start_time, T)
            continue
        if frame.arb_id not in T.keys():
            T[frame.arb_id] = [frame]
        else:
            T[frame.arb_id] += [frame]

        update_t(start_time, T)


# reference: https://support.vector.com/kb?id=kb_article_view&sysparm_article=KB0012332&sys_kb_id=99354e281b2614148e9a535c2e4bcb6d&spa=1
def calculate_bus_load(baudrate=500000):
    sum = 0
    for _, frame_list in T.items():
        if not frame_list:
            continue
        for frame in frame_list:
            sum = sum + 11 if not frame.is_extended_id else sum + 29
            sum += (
                1 + 1 + 6 + len(frame.data) * 8 + 15 + 10 + 3 + 7 + 3
            )  # 10 is an estimate of bit stuffing

    return "{:.2f}".format(sum / 5.0 / float(baudrate) * 100)


def draw_table(stdscr, dev, T, DBC):
    value = 0
    k = 0
    fps = 0
    offset = 0
    binary = False
    cursor_x, cursor_y = 0, 1
    expanded_arb_ids = {}

    stdscr = curses.initscr()
    stdscr.nodelay(True)
    curses.start_color()
    curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_WHITE)

    frame_counter = 0
    start_time = time.time()
    while k != ord("q"):
        if not T:
            continue
        height, width = stdscr.getmaxyx()
        if k == ord("b"):  # binary/normal mode switch
            binary = not binary
        elif k == ord("e"):  # show/hide signal detail
            line = stdscr.instr(27).decode()
            if line[0] in ["+", "-"]:
                arb_id = int(line.strip().split(" ")[-1], 16)
                if arb_id not in expanded_arb_ids.keys():
                    expanded_arb_ids[arb_id] = True
                else:
                    expanded_arb_ids[arb_id] = not expanded_arb_ids[arb_id]

        # update cursor position
        elif k == curses.KEY_DOWN:
            cursor_y += 1
        elif k == curses.KEY_UP:
            cursor_y -= 1
        elif k == curses.KEY_RIGHT:
            cursor_x += 1
        elif k == curses.KEY_LEFT:
            cursor_x -= 1
        elif cursor_y == height - 1:
            cursor_y = height - 2
            offset += 1
        elif cursor_y == 0:
            cursor_y = 1
            offset = max(0, offset - 1)
        cursor_x = max(0, cursor_x)
        cursor_x = min(width - 1, cursor_x)

        table = []
        for arb_id, frame_list in sorted(T.items()):
            if not frame_list:
                continue
            frame = frame_list[-1]  # get the latest frame

            data = parse_data(frame.data, binary)
            row = "{:<10.3f} {:<6s} {:<8s} {:<25s} {}".format(
                frame.timestamp, dev.ndev, hex(arb_id)[2:], data, len(frame_list) / 5
            )
            if (
                arb_id in DBC.keys()
                and arb_id in expanded_arb_ids.keys()
                and expanded_arb_ids[arb_id] == True
            ):
                table.append("-" + row)
                message = parse_frame(frame.data, DBC[arb_id]["signals"])
                for name, signal in message.items():
                    table.append("|---{}: {} {}".format(name, *signal.values()))

            elif arb_id in DBC.keys():
                table.append("+" + row)
            else:
                table.append(" " + row)

        stdscr.clear()
        stdscr.addstr(
            0,
            0,
            " {:<10s} {:<6s} {:<8s} {:<25s} {}".format(
                "Time", "Dev", "ID", "Data", "FPS"
            ),
        )
        for index, line in enumerate(table[offset : offset + height - 2]):
            stdscr.addstr(index + 1, 0, line)

        # Rendering status bar
        stdscr.attron(curses.color_pair(1))
        status_bar_str = "Press 'q' to exit | Bus Load: {}% | FPS: {}".format(
            calculate_bus_load(), fps
        )
        stdscr.addstr(height - 1, 0, status_bar_str)
        stdscr.addstr(
            height - 1, len(status_bar_str), " " * (width - len(status_bar_str) - 1)
        )
        stdscr.attroff(curses.color_pair(1))

        frame_counter += 1
        if time.time() - start_time > 1:
            fps = frame_counter
            frame_counter = 0
            start_time = time.time()

        stdscr.move(cursor_y, cursor_x)
        time.sleep(0.01)
        k = stdscr.getch()


def sniff(dev, dbc: str = None) -> None:
    traffic_handler_process = Process(target=traffic_handler, args=[dev, T])
    traffic_handler_process.start()
    DBC = dbc_to_dict(dbc) if dbc else {}
    curses.wrapper(draw_table, dev, T, DBC)
