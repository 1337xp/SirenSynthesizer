import numpy as np
from scipy.signal import chirp, sweep_poly
from scipy.io.wavfile import write
from scipy.signal import butter, lfilter, freqz
import matplotlib.pyplot as plt
from scipy import signal
import sounddevice as sd
fs = 44100
RATE = 30
def risecurve(time: float = 10, rpm: float = None, type = "1ph", ports: int = 10, hz: int = 60):
    n = int(time * fs)
    if type == "1ph":

        t1 = np.linspace(0, -1/time, n, endpoint=True)
        t2 = np.linspace(-1, 0, n, endpoint=False)
        t3 = np.linspace(-1, -0.5 , n, endpoint=False)
        data = -t3**2 + 1
        volumecurve = -t2**2 + 1
        return (np.sin(2 * np.pi * (ports * ((((data * 0.8) * rpm)) * time) * time / hz) * t1) * (volumecurve))
    if type == "3ph":
        t1 = np.linspace(0, 1/time, n, endpoint=False)
        return np.sin(2 * np.pi * (ports * (((t1 * rpm) / 2) * time) * time / hz) * t1)
    else:
        return None
chunk = 2048
def fallcurve(time: float = 10, rpm: float = None, type = "1ph", ports: int = 10, hz: int = 60):
    n = int(time * fs)
    t2 = np.linspace(1/time, 0, n, endpoint=False)
def fullrpm(time: float = 10, rpm: float = None, ports: int = 10):
    n = int(time * fs)
    t2 = np.linspace(0, 1/time, n, endpoint=False)
write("test3.wav", 44100, risecurve(rpm=3450.0,time=10, ports=10))