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
        t2 = np.linspace(-1, 0, n, endpoint=False)
        data = t1 * time
        volumecurve = -t2 ** 2 + 1
        return np.sin(2 * np.pi * ((ports * (((data * rpm) / 2) * time) * time / hz) * t1)) * volumecurve
    else:
        return None
chunk = 2048
def fallcurve(time: float = 10, rpm: float = None, type = "1ph", ports: int = 10, hz: int = 60):
    n = int(time * fs)
    if type == "1ph":

        t1 = np.linspace(-1/time, 0 , n, endpoint=True)
        t2 = np.linspace(0, -1, n, endpoint=False)
        t3 = np.linspace(-0.699953, 0, n, endpoint=False)
        data = -t3**4
        volumecurve = -t2**2 + 1
        return (np.sin(2 * np.pi * (ports * ((((data * 0.8) * rpm)) * time) * time / hz) * t1) * (volumecurve))
    if type == "3ph":
        t1 = np.linspace(1/time, 0, n, endpoint=False)
        t2 = np.linspace(0, -1, n, endpoint=False)
        data = t1 * time
        volumecurve = -t2 ** 2 + 1
        return np.sin(2 * np.pi * ((ports * (((data * rpm) / 2) * time) * time / hz) * t1)) * volumecurve
    else:
        return None
def fullrpm(time: float = 10, rpm: float = None, ports: int = 10, hz: int = 60):
    n = int(time * fs)
    t1 = np.linspace(0, 1/time, n, endpoint=False)
    return np.sin(2 * np.pi * (ports * (rpm * time) / hz) * time * t1)
x = np.append(risecurve(rpm=3450.0,time=3, ports=10, type="3ph"),-fullrpm(rpm=3450.0,time=10, ports=10))
x = np.append(x,fallcurve(time=30, rpm=3450.0, type="1ph", ports=10))
write("test3.wav", fs, x)