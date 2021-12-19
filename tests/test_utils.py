import pytest

from canst.can import Frame
from canst.utils import *


def test_frame_data_to_str():

    data1 = [65, 7, 133, 28, 0, 128, 0, 0]
    data2 = [255, 255, 255, 255, 255, 255, 255, 255]

    assert frame_data_to_str(data1) == "4107851c00800000"
    assert frame_data_to_str(data2) == "ffffffffffffffff"
