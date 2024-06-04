import pytest

from web_renderer.utils.datetime import get_timestamp


def test_get_timestamp():
    assert isinstance(get_timestamp(), float)
