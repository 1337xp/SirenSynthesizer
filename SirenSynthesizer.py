import numpy as np
from scipy.signal import chirp, sweep_poly
from scipy.io.wavfile import write
from scipy.signal import butter, lfilter, freqz
import matplotlib.pyplot as plt
from scipy import signal
import sounddevice as sd
fs = 44100
RATE = 30
hilo = True
rpm = 6960
windup_time = 4
still_time = 20
winddown_time = 20
totaltime = windup_time + still_time
def risecurve(time: float = 10, rpm: float = None, type = "1ph", ports: int = 10, hz: int = 60):
    n = int(time * fs)
    if type == "1ph":

        t1 = np.linspace(0, -1/time, n, endpoint=True)
        t2 = np.linspace(-1, 0, n, endpoint=False)
        t3 = np.linspace(-1, -0.5 , n, endpoint=False)
        data = -t3**2 + 1
        volumecurve = -t2**2 + 1
        return (signal.sawtooth(2 * np.pi * (ports * ((((data * 0.8) * rpm)) * time) * time / hz) * t1) * (volumecurve))
    if type == "3ph":
        t1 = np.linspace(0, 1/time, n, endpoint=False)
        t2 = np.linspace(-1, 0, n, endpoint=False)
        data = t1 * time
        volumecurve = -t2 ** 2 + 1
        return signal.sawtooth(2 * np.pi * ((ports * (((data * rpm) / 2) * time) * time / hz) * t1)) * volumecurve
    else:
        return None
chunk = 2048
def fallcurve(time: float = 10, rpm: float = None, type = "1ph", ports: int = 10, hz: int = 60):
    n = int(time * fs)
    if type == "1ph":

        t1 = np.linspace(-1/time, 0 , n, endpoint=True)
        t2 = np.linspace(0, -1, n, endpoint=False)
        t3 = np.linspace(-0.706, 0, n, endpoint=False)
        data = -t3**4
        volumecurve = -t2**2 + 1
        return (signal.sawtooth(2 * np.pi * (ports * ((((data * 0.8) * rpm)) * time) * time / hz) * t1) * (volumecurve))
    if type == "3ph":
        t1 = np.linspace(1/time, 0, n, endpoint=False)
        t2 = np.linspace(0, -1, n, endpoint=False)
        data = t1 * time
        volumecurve = -t2 ** 2 + 1
        return signal.sawtooth(2 * np.pi * ((ports * (((data * rpm) / 2) * time) * time / hz) * t1)) * volumecurve
    else:
        return None
def hilo(time: int = 16, rpm: float = None, type = "1ph", sus: int = 1, hz: int = 60):
    n = int((time/44100) * fs)
    t1 = np.linspace(0, int((time/44100)), time, endpoint=False)
    n = int((time/44100) * fs)
    if type == "1ph":
        t2 = np.linspace(-1, -0.5, time, endpoint=False)
        volumecurve = -t2**24 + 1
    if sus == 1:
        return ((-signal.square(2 * np.pi * volumecurve * t1) + 1.3) / 2)
    else:
        return ((signal.square(2 * np.pi * volumecurve * t1) + 1.3) / 2)
def fullrpm(time: float = 10, rpm: float = None, ports: int = 10, hz: int = 60):
    n = int(time * fs)
    t1 = np.linspace(0, 1/time, n, endpoint=False)
    return signal.sawtooth(2 * np.pi * (ports * (rpm * time) / hz) * time * t1)

#x = np.append(risecurve(rpm=rpm,time=windup_time, ports=12, type="1ph"),-fullrpm(rpm=rpm,time=still_time, ports=12))
# 2.1 for 3ph and 2.9 for 1ph
x = np.append(risecurve(rpm=rpm, time=windup_time, ports=6, type="1ph")[int((windup_time * fs) / 2.9):],-fullrpm(rpm=rpm, time=still_time / 6, ports=6))
x = x * hilo(x.size, sus=0)
x = np.append(x,-fallcurve(time=winddown_time, rpm=rpm, type="1ph", ports=6)[:int((winddown_time * fs) / 6)])
for i in range(2):
    x = np.append(x,x)
#y = np.append(risecurve(rpm=rpm,time=windup_time, ports=10, type="1ph"),-fullrpm(rpm=rpm,time=still_time, ports=10))

y =np.append(risecurve(rpm=rpm,time=windup_time, ports=5, type="1ph")[int((windup_time * fs) / 2.9):],-fullrpm(rpm=rpm,time=still_time / 6, ports=5))
y = y * hilo(y.size, sus=0)
y = np.append(y,-fallcurve(time=winddown_time, rpm=rpm, type="1ph", ports=5)[:int((winddown_time * fs) / 6)])
for i in range(2):
    y = np.append(y,y)


y = y
x = x
x = x + y

write("test3.wav", fs, x)
