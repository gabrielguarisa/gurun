import time


def test_sleep():
    from gurun.utils import Sleep

    expected = 0.5

    node = Sleep(expected, verbose=3)

    start_time = time.time()
    node.run()
    end_time = time.time()

    assert end_time - start_time >= expected
