from scipy.signal import butter, filtfilt, stft
from scipy.fft import fft, fftfreq
import numpy as np
import pandas as pd


def _butter_bandpass(lowcut, highcut, fs, order=5):
    nyq = 0.5 * fs
    low = lowcut / nyq
    high = highcut / nyq
    b, a = butter(order, [low, high], btype='bandpass')
    return b, a

#def _low_pass(data, lowcut, highcut, fs, )

def butter_bandpass_filter(data, lowcut, highcut, fs, order=4):
    b, a = _butter_bandpass(lowcut, highcut, fs, order=order)
    filterd_data = filtfilt(b, a, data)
    
    #emg_rectified = abs(filterd_data)
    #emg_envelope = emg_rectified
    # create lowpass filter and apply to rectified signal to get EMG envelope
    #low_pass = lowcut/(fs/2)
    #b2, a2 = butter(4, low_pass, btype='lowpass')
    #emg_envelope = filtfilt(b2, a2, emg_rectified)
    
    return filterd_data


def fast_fourier(series:pd.Series, timewindow:float=0.5, timeshift:float=0.01, fs=1500):
    nperseg = timewindow*fs
    noverlap = (timewindow-timeshift)*fs
    f, t, Zxx = stft(series, fs, nperseg=nperseg, noverlap=noverlap)
    return f, t, Zxx
