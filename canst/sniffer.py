import time
import struct
import curses
import binascii
from multiprocessing import Process, Manager

from .utils import *

T = Manager().dict()

# TODO: needs to be fixed
def get_value(signal, data):
    v = "".join("{0:08b}".format(i) for i in data)
    v = v[signal["start"] : signal["start"] + signal["length"]]
    v = int(v, 2)
    v = struct.pack("@h", v)
    v = int(binascii.hexlify(v).decode(), 16)
    v = signal["offset"] + signal["factor"] * v

    return v


def parse_data(data, mode):
    if mode:
        data_str = " ".join("{0:08b}".format(i) for i in data)
    else:
        data_str = " ".join("{0:02x}".format(i) for i in data)

    return data_str


def traffic_handler(dev, T):
    while True:
        frame = dev.recv()
        T[frame.arb_id] = frame


def draw_table(stdscr, dev, T, DBC):
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
            line = stdscr.instr(26).decode()
            if line[0] == "+":
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
        for arb_id, frame in sorted(T.items()):
            data = parse_data(frame.data, binary)
            row = " {:<10.3f} {:<6s} {:<8s} {}".format(
                frame.timestamp, dev.ndev, hex(arb_id)[2:], data
            )
            if arb_id in DBC.keys():
                row = "+{:<10.3f} {:<6s} {:<8s} {}".format(
                    frame.timestamp, dev.ndev, hex(arb_id)[2:], data
                )
            table.append(row)
            if arb_id in expanded_arb_ids.keys() and expanded_arb_ids[arb_id] == True:
                for name, signal in DBC[arb_id]["signals"].items():
                    value = get_value(signal, frame.data)
                    unit = signal["unit"] if signal["unit"] else ""
                    table.append("|---{}: {} {}".format(name, value, unit))

        stdscr.clear()
        stdscr.addstr(
            0, 0, " {:<10s} {:<6s} {:<8s} {}".format("Time", "Dev", "ID", "Data")
        )
        for index, line in enumerate(table[offset : offset + height - 2]):
            stdscr.addstr(index + 1, 0, line)

        # Rendering status bar
        stdscr.attron(curses.color_pair(1))
        status_bar_str = "Press 'q' to exit | POS: {}, {} | FPS: {}".format(
            cursor_x, cursor_y, fps 
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
        time.sleep(0.02)
        k = stdscr.getch()


def sniff(dev, file_path: str = None) -> None:
    traffic_handler_process = Process(target=traffic_handler, args=[dev, T])
    traffic_handler_process.start()
    DBC = dbc_to_dict(file_path) if file_path else {}
    curses.wrapper(draw_table, dev, T, DBC)
