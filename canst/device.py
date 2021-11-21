from .can import SocketCanDev


def init_dev(device_name):
    global dev
    dev = SocketCanDev(device_name)
    dev.start()

    return dev
