import InterruptibleSleepBinding
import signal, time

def custom_sleep(duration: int):
    response: int = InterruptibleSleepBinding.sleep_for_x_milliseconds(int(duration)*1000)
    if(response!=-1):
        signal.raise_signal(response)

time.sleep = custom_sleep