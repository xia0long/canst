import time
import struct
import socket

from dataclasses import dataclass

class FrameType:
    DataFrame = 1
    RemoteFrame = 2
    ErrorFrame = 3
    OverloadFrame = 4


@dataclass
class Frame:
    arb_id: int
    data: list = None
    frame_type: FrameType = 1
    interface: str = None
    timestamp: float = None
    is_extended_id: bool = False

    @property
    def dlc(self):
        return len(self.data)


class SocketCanDev:
    def __init__(self, ndev):
        self.running = False

        if not hasattr(socket, "PF_CAN") or not hasattr(socket, "CAN_RAW"):
            print("Python 3.3 or later is needed for native SocketCAN")
            raise SystemExit(1)

        self.socket = socket.socket(socket.PF_CAN, socket.SOCK_RAW, socket.CAN_RAW)
        self.ndev = ndev

    def start(self):
        self.socket.bind((self.ndev,))
        self.start_time = time.time()
        self.running = True

    def recv(self):
        assert self.running, "device is not running"
        frame_format = "=IB3xBBBBBBBB"
        frame_size = struct.calcsize(frame_format)

        frame_raw = self.socket.recv(frame_size)
        arb_id, dlc, d0, d1, d2, d3, d4, d5, d6, d7 = struct.unpack(
            frame_format, frame_raw
        )

        is_extended_id = False
        if arb_id & 0x80000000:
            arb_id &= 0x7FFFFFFF
            is_extended_id = True

        frame = Frame(arb_id, is_extended_id=is_extended_id)
        frame.data = [d0, d1, d2, d3, d4, d5, d6, d7][0:dlc]
        frame.timestamp = time.time() - self.start_time

        return frame

    def send(self, frame):
        assert self.running, "device is not running"
        frame_format = "=IBBBBBBBBBBBB"

        arb_id = frame.arb_id
        if frame.is_extended_id:
            arb_id |= 0x80000000

        data = frame.data + [0] * (8 - len(frame.data))
        packet = struct.pack(
            frame_format,
            arb_id,
            frame.dlc,
            0xFF,
            0xFF,
            0xFF,
            data[0],
            data[1],
            data[2],
            data[3],
            data[4],
            data[5],
            data[6],
            data[7],
        )
        self.socket.send(packet)
