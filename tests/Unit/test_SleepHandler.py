import time

def test_sleep_call_count(mocker):
    mocked = mocker.patch("InterruptibleSleepBinding.sleep_for_x_milliseconds", return_value=-1)
    time.sleep(1)
    assert(mocked.call_count == 1)
    
def test_sleep_duration():
    initial_time = time.time()
    time.sleep(1)
    assert(time.time() - initial_time > 0.9)
