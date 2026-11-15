import time

import pytest

from hces.timing import RunClock


def test_spans_and_peak_memory():
    with RunClock() as clock:
        with clock.span("access"):
            time.sleep(0.01)
        with clock.span("analysis"):
            blob = bytearray(40 * 1024 * 1024)  # 40 MB, held briefly
            time.sleep(0.1)
            del blob
        with clock.span("response"):
            pass
    clock.require("access", "analysis", "response")
    assert clock.ms["access"] >= 9
    assert clock.peak_rss_mb > 40


def test_unknown_and_repeated_spans_refused():
    clock = RunClock()
    with pytest.raises(ValueError):
        with clock.span("lunch"):
            pass
    with clock.span("access"):
        pass
    with pytest.raises(ValueError):
        with clock.span("access"):
            pass


def test_missing_timing_is_reported():
    clock = RunClock()
    with pytest.raises(RuntimeError, match="response"):
        clock.require("response")
