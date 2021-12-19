import sys
from datetime import datetime

import click

from .constants import *
from .device import init_dev
from .dumper import dump
from .sniffer import sniff
from .sender import send
from .fuzzer import random_fuzz, mutate_fuzz


def exit_early(ctx, param, value):
    if value:
        sys.exit()


print("canst v0.1.0\n")

CONTEXT_SETTINGS = dict(help_option_names=["-h", "--help"])


@click.group(context_settings=CONTEXT_SETTINGS)
@click.option(
    "-i", "--interface", type=str, default="can0", help="Choose CAN bus interface."
)
def canst(interface):
    """The entry point for canst."""
    global dev
    dev = init_dev(interface)


@canst.command(help="Dump CAN bus traffic.")
@click.option("--arb_id_filter", type=str, default=None, help="Filter by CAN ID.")
@click.option("--data_filter", type=str, default=None, help="Filter by CAN data.")
@click.option(
    "-l",
    "--log_path",
    type=str,
    is_flag=True,
    default=None,
    help="File to write to.",
)
def dumper(arb_id_filter, data_filter, log_path):
    if log_path:
        log_path = "candump-{}.log".format(datetime.now().strftime("%Y-%m-%d_%H_%M_%S"))
    dump(dev, arb_id_filter, data_filter, log_path)


@canst.command(help="Sniff CAN bus traffic.")
@click.option("--dbc", type=str, default=None, help="DBC file to read from.")
def sniffer(dbc):
    sniff(dev, dbc)


@canst.command(help="Send CAN bus traffic.")
@click.option("-m", "--messages", default=list, multiple=True, help="Message to send.")
@click.option(
    "-d",
    "--delays",
    type=float,
    default=list,
    multiple=True,
    help="Delay between sending messages.",
)
@click.option("-fp", "--file_path", type=str, default=None, help="File to read from.")
@click.option(
    "--start_line", type=int, default=None, help="The start line number read from file."
)
@click.option(
    "--end_line", type=int, default=None, help="The end line number read from file."
)
@click.option("-l", "--loop", is_flag=True, help="Loop sending messages.")
def sender(messages, delays, file_path, start_line, end_line, loop):
    send(dev, messages, delays, file_path, start_line, end_line, loop)


@canst.group(help="CAN message fuzzing tool.")
def fuzzer():
    pass


@fuzzer.command(help="Generate random messages and send them.")
@click.option("--arb_id_filter", type=str, default=None, help="Filter by CAN ID.")
@click.option("--data_filter", type=str, default=None, help="Filter by CAN data.")
@click.option(
    "--min_arb_id",
    type=str,
    default=hex(MIN_ARB_ID)[2:],
    help="Specify the minimum arbitration id to fuzz.",
)
@click.option(
    "--max_arb_id",
    type=str,
    default=hex(MAX_ARB_ID)[2:],
    help="Specify the maximum arbitration id to fuzz.",
)
@click.option(
    "--min_data_len",
    default=MIN_DATA_LEN,
    help="Specify the minimum data length to fuzz.",
)
@click.option(
    "--max_data_len",
    default=MAX_DATA_LEN,
    help="Specify the maximum data length to fuzz.",
)
@click.option("-d", "--delay", default=DELAY, help="Delay between sending messages.")
def random(
    arb_id_filter,
    data_filter,
    min_arb_id,
    max_arb_id,
    min_data_len,
    max_data_len,
    delay,
):
    random_fuzz(
        dev,
        arb_id_filter,
        data_filter,
        min_arb_id,
        max_arb_id,
        min_data_len,
        max_data_len,
        delay,
    )


@fuzzer.command(help="Generate mutate messages and send them.")
@click.option(
    "-m", "--message", type=str, default=None, help="Specify the init message to fuzz"
)
@click.option("-d", "--delay", default=DELAY, help="Delay between sending messages.")
def mutate(message, delay):
    mutate_fuzz(dev, message, delay)


if __name__ == "__main__":
    canst()
