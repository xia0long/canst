import pytest

from canst.can import Frame
from canst.sender import get_frame_list_from_file


def test_get_frame_list_from_file():

    frame_list = get_frame_list_from_file(
        file_path="tests/data/candump.log", start_line=10, end_line=12
    )

    assert frame_list == [
        (
            Frame(
                arb_id=280,
                data=[65, 7, 133, 28, 0, 128, 0, 0],
                frame_type=1,
                interface=None,
                timestamp=None,
                is_extended_id=False,
            ),
            0.0002889999999999837,
        ),
        (
            Frame(
                arb_id=599,
                data=[190, 68, 31, 0, 2, 0, 0, 0],
                frame_type=1,
                interface=None,
                timestamp=None,
                is_extended_id=False,
            ),
            0.0002869999999999262,
        ),
        (
            Frame(
                arb_id=545,
                data=[97, 5, 5, 0, 0, 0, 192, 78],
                frame_type=1,
                interface=None,
                timestamp=None,
                is_extended_id=False,
            ),
            0.000288000000000066,
        ),
    ]
