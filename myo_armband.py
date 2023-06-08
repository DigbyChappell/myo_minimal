"""
myo_armband.py - Digby Chappell, July 2022
Processes muscle activity data from a Myo Armband (Thalmic Labs). Heavily borrowed from Niklas Rosenstein's 2017 work.
"""

from collections import deque
from threading import Lock, Thread

import myo
import numpy as np


class MyoStream(myo.DeviceListener):
    """
    Collects EMG data in a queue with *n* maximum number of elements.
    """
    def __init__(self, n):
        self.n = n
        self.lock = Lock()
        self.emg_data_queue = deque(maxlen=n)

    def get_emg_data(self):
        with self.lock:
            return list(self.emg_data_queue)

    def on_connected(self, event):
        event.device.stream_emg(True)

    def on_emg(self, event):
        with self.lock:
            self.emg_data_queue.append((event.timestamp, event.emg))


class GetSample(object):
    def __init__(self, listener):
        self.n = listener.n
        self.listener = listener
        self.emg_data = []

    def update_sample(self):
        self.emg_data = self.listener.get_emg_data()
        self.emg_data = np.array([x[1] for x in self.emg_data]).T
        self.emg_data = abs(self.emg_data)/128

    def main(self):
        while True:
            self.update_sample()
            # print(self.emg_data)


def main():
    myo.init(lib_name='C:/Program Files (x86)/Thalmic Labs/myo-sdk-win-0.9./lib',
             bin_path='C:/Program Files (x86)/Thalmic Labs/myo-sdk-win-0.9./bin/myo64.dll')
    hub = myo.Hub()
    listener = MyoStream(20)
    with hub.run_in_background(listener.on_event, 5):
        GetSample(listener).main()


if __name__ == '__main__':
    main()
