import InterruptibleSleepBinding
import signal

class SleepHandlerClass:
    def sleep(self, duration: int):
        response: int = InterruptibleSleepBinding.sleep_for_x_milliseconds(duration)
        if(response!=-1):
            signal.raise_signal(response)

SLEEPHANDLER = SleepHandlerClass()