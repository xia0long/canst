import time
import curses
from multiprocessing import Process, Manager

from .utils import *

T = Manager().dict()
stdscr = curses.initscr()
stdscr.nodelay(True)


def traffic_handler(dev, T):
    while True:
        frame = dev.recv()
        T[frame.arb_id] = frame


def draw_table(stdscr, dev, T):
    k = 0
    fps = 0
    cursor_x = 0
    cursor_y = 0
    bs = False

    curses.start_color()
    curses.init_pair(1, curses.COLOR_CYAN, curses.COLOR_BLACK)
    curses.init_pair(2, curses.COLOR_RED, curses.COLOR_BLACK)
    curses.init_pair(3, curses.COLOR_BLACK, curses.COLOR_WHITE)

    frame_counter = 0
    start_time = time.time()
    while k != ord("q"):
        if not T:
            continue
        stdscr.clear()
        height, width = stdscr.getmaxyx()

        if k == ord("b"):
            bs = not bs

        # update cursor pisition
        if k == curses.KEY_DOWN:
            cursor_y = cursor_y + 1
        if k == curses.KEY_UP:
            cursor_y = cursor_y - 1
        if k == curses.KEY_RIGHT:
            cursor_x = cursor_x + 1
        if k == curses.KEY_LEFT:
            cursor_x = cursor_x - 1

        cursor_x = max(0, cursor_x)
        cursor_x = min(width - 1, cursor_x)

        cursor_y = max(0, cursor_y)
        cursor_y = min(height - 1, cursor_y)

        stdscr.addstr(
            0, 0, " {:<8s} {:<6s} {:<6s} {:<}".format("Time", "Dev", "ID", "Data")
        )
        offset = 2
        for arb_id, frame in dict(sorted(T.items())).items():
            if bs:
                data = " ".join(bin(i)[2:] for i in frame.data)
            else:
                data = " ".join(hex(i)[2:] for i in frame.data)

            row = " {:<8.3f} {:<6s} {:<6s} {}".format(
                frame.timestamp, dev.ndev, hex(arb_id)[2:], data
            )
            stdscr.addstr(offset, 0, row)
            offset += 1

        frame_counter += 1
        if time.time() - start_time > 1:
            fps = frame_counter
            frame_counter = 0
            start_time = time.time()

        # Rendering status bar
        stdscr.attron(curses.color_pair(3))
        status_bar_str = "Press 'q' to exit | POS: {}, {} | FPS: {}".format(
            cursor_x, cursor_y, fps
        )
        stdscr.addstr(height - 1, 0, status_bar_str)
        stdscr.addstr(
            height - 1, len(status_bar_str), " " * (width - len(status_bar_str) - 1)
        )
        stdscr.attroff(curses.color_pair(3))

        stdscr.move(cursor_y, cursor_x)
        time.sleep(0.02)
        stdscr.refresh()
        k = stdscr.getch()


def sniff(dev) -> None:
    traffic_handler_process = Process(target=traffic_handler, args=[dev, T])
    traffic_handler_process.start()
    curses.wrapper(draw_table, dev, T)
