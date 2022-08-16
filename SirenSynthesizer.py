import numpy as np
import random as rnd
from scipy.io.wavfile import write
from scipy import signal
from scipy.signal import butter, lfilter, freqz
from pysndfx import AudioEffectsChain

fx = (
    AudioEffectsChain()
    .highshelf()
    .reverb()
    .phaser()
    .delay()
    .lowshelf()
)
fs = 44100
RATE = 30
hilo = True
rpm = 2880
hz = 50
hilorate = 0.4
windup_time = 5
motortype = "3ph"
still_time = 10
winddown_time = 50
totaltime = windup_time + still_time

ports = [10, 12]

# 0 = Alert, 1 = Attack, 2 = HiLo, 3 = Pulse, 4 = Wailing HiLo, 5 = Wailing Pulse
FScontroller = 4

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
        t3 = np.linspace(-0.70556, 0, n, endpoint=False)
        data = -t3**4
        volumecurve = -t2**4 + 1
        return (signal.sawtooth(2 * np.pi * (ports * ((((data * 0.8) * rpm)) * time) * time / hz) * t1) * (volumecurve))
    if type == "3ph":
        t1 = np.linspace(1/time, 0, n, endpoint=False)
        t2 = np.linspace(0, -1, n, endpoint=False)
        data = t1 * time
        volumecurve = -t2 ** 4 + 1
        return signal.sawtooth(2 * np.pi * ((ports * (((data * rpm) / 2) * time) * time / hz) * t1)) * volumecurve
    else:
        return None
def hilo(time: int = 16, type = "1ph", sus: int = 1, rate: int = 1):
    n = int((time/44100) * fs)
    t1 = np.linspace(0, int((time/44100)), time, endpoint=False)
    n = int((time/44100) * fs)
    if type == "1ph":
        t2 = np.linspace(-1, -0.5, time, endpoint=False)
        volumecurve = -t2**12 + 1
    if sus == 1:
        return ((-signal.square(2 * np.pi * (volumecurve * rate) * t1) + 1.02) / 2)
    else:
        return ((signal.square(2 * np.pi * (volumecurve * rate) * t1) + 1.02) / 2)
def fullrpm(time: float = 10, rpm: float = None, ports: int = 10, hz: int = 60):
    n = int(time * fs)
    t1 = np.linspace(0, 1/time, n, endpoint=False)
    return signal.sawtooth(2 * np.pi * (ports * (rpm * time) / hz) * time * t1)
if FScontroller <= 3:
    x = risecurve(time=windup_time,ports=ports[0], rpm=rpm, type=motortype,hz=hz),
    x = np.append(x, fullrpm(time=still_time,ports=ports[0], rpm=rpm,hz=hz))

    if FScontroller == 2:
        x = x * hilo(x.size, sus=0, rate=hilorate)
    elif FScontroller == 3:
        x = x * hilo(x.size, sus=1, rate=hilorate)
    x = np.append(x, fallcurve(time=winddown_time, ports=ports[0], rpm=rpm, type="1ph", hz=hz))
    y = risecurve(time=windup_time,ports=ports[1], rpm=rpm, type=motortype,hz=hz),
    y = np.append(y, fullrpm(time=still_time,ports=ports[1], rpm=rpm,hz=hz))

    if FScontroller == 2 or FScontroller == 3:
        y = y * hilo(y.size, sus=1,rate=hilorate)
    y = np.append(y, fallcurve(time=winddown_time, ports=ports[1], rpm=rpm, type="1ph", hz=hz))
    if FScontroller == 1:
        x = np.append(risecurve(rpm=rpm,time=windup_time, ports=ports[1], type=motortype),-fullrpm(rpm=rpm,time=still_time, ports=ports[1]))
        x = np.append(x,-fallcurve(time=winddown_time, rpm=rpm, type="1ph", ports=ports[1])[:int((winddown_time * fs) / 6)])
        # 2.1 for 3ph and 2.9 for 1ph

        x1 = np.append(risecurve(rpm=rpm, time=windup_time, ports=ports[1], type=motortype)[int((windup_time * fs) / 2.1):],
                  -fullrpm(rpm=rpm, time=still_time, ports=ports[1]))
        x1 = np.append(x1, -fallcurve(time=winddown_time, rpm=rpm, type="1ph", ports=ports[1])[:int((winddown_time * fs) / 6)])
        for i in range(3):
            x1 = np.append(x1, x1)
        x = np.append(x, x1)
        y = np.append(risecurve(rpm=rpm,time=windup_time, ports=ports[0], type=motortype),-fullrpm(rpm=rpm,time=still_time, ports=ports[0]))
        y = np.append(y,-fallcurve(time=winddown_time, rpm=rpm, type="1ph", ports=ports[0])[:int((winddown_time * fs) / 6)])
        y1 = np.append(risecurve(rpm=rpm, time=windup_time, ports=ports[0], type=motortype)[int((windup_time * fs) / 2.1):],
                      -fullrpm(rpm=rpm, time=still_time, ports=ports[0]))
        if FScontroller == 2 or FScontroller == 3:
            y1 = y1 * hilo(y1.size, sus=1, rate=hilorate)
        y1 = np.append(y1, -fallcurve(time=winddown_time, rpm=rpm, type="1ph", ports=ports[0])[:int((winddown_time * fs) / 6)])
        for i in range(3):
           y1 = np.append(y1, y1)
        y = np.append(y, y1)
if FScontroller == 4 or FScontroller == 5:
    x = np.append(risecurve(rpm=rpm,time=windup_time, ports=ports[1], type=motortype),-fullrpm(rpm=rpm,time=still_time, ports=ports[1]))
    x = np.append(x,-fallcurve(time=winddown_time, rpm=rpm, type="1ph", ports=ports[1])[:int((winddown_time * fs) / 6)])
    # 2.1 for 3ph and 2.9 for 1ph

    x1 = np.append(risecurve(rpm=rpm, time=windup_time, ports=ports[1], type=motortype)[int((windup_time * fs) / 2.1):],
                -fullrpm(rpm=rpm, time=still_time, ports=ports[1]))
    if FScontroller == 4:
        x1 = x1 * hilo(x1.size, sus=1, rate=hilorate)
    elif FScontroller == 5:
        x1 = x1 * hilo(x1.size, sus=0, rate=hilorate)
    x1 = np.append(x1, -fallcurve(time=winddown_time, rpm=rpm, type="1ph", ports=ports[1])[:int((winddown_time * fs) / 6)])

    for i in range(3):
        x1 = np.append(x1, x1)
    x = np.append(x, x1)
    y = np.append(risecurve(rpm=rpm,time=windup_time, ports=ports[0], type=motortype),-fullrpm(rpm=rpm,time=still_time, ports=ports[0]))
    y = np.append(y,-fallcurve(time=winddown_time, rpm=rpm, type="1ph", ports=ports[0])[:int((winddown_time * fs) / 6)])
    y1 = np.append(risecurve(rpm=rpm, time=windup_time, ports=ports[0], type=motortype)[int((windup_time * fs) / 2.1):],
                    -fullrpm(rpm=rpm, time=still_time, ports=ports[0]))
    if FScontroller == 5 or FScontroller == 4:
        y1 = y1 * hilo(y1.size, sus=0, rate=hilorate)
    y1 = np.append(y1, -fallcurve(time=winddown_time, rpm=rpm, type="1ph", ports=ports[0])[:int((winddown_time * fs) / 6)])
    for i in range(3):
        y1 = np.append(y1, y1)
    y = np.append(y, y1)




def butter_lowpass(cutoff, fs, order=5):
    nyq = 0.5 * fs
    normal_cutoff = cutoff / nyq
    b, a = butter(order, normal_cutoff, btype='low', analog=False)
    return b, a

def butter_lowpass_filter(data, cutoff, fs, order=5):
    b, a = butter_lowpass(cutoff, fs, order=order)
    y = lfilter(b, a, data)
    return y



order = 2
fs1 = 44100.0
cutoff1 = 4590
cutoff2 = 2590
b, a = butter_lowpass(cutoff1, fs, order)
x12 = np.linspace(0, rnd.randint(440, 1995), x.size)
x13 = np.linspace(0, rnd.randint(210, 1795), x.size)
x14 = np.linspace(0, rnd.randint(78, 1125), x.size)
def f(x):
    return np.sin(x) + np.random.normal(scale=0.1, size=len(x))
y = butter_lowpass_filter(y, cutoff1, fs1, order) * 0.3
x = butter_lowpass_filter(x, cutoff1, fs1, order) * 0.3
y = butter_lowpass_filter(y, cutoff1, fs1, order)
x = butter_lowpass_filter(x, cutoff1, fs1, order)
x = x * ((butter_lowpass_filter(f(x14) + f(x13) * f(x12), 20, fs1, 1)/ 50) + 0.4) + y * ((butter_lowpass_filter(f(x12) + f(x13) * f(x14), 20, fs1, 1)/ 50) + 0.4)
x = x * ((butter_lowpass_filter(f(x14) + f(x13) * f(x14), 20, fs1, 1)/ 48) + 0.3)
x = fx(x)
write("test3.wav", fs, x)
