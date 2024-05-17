### Fast fourier transformation ###

import pandas as pd
import numpy as np

from scipy.signal import butter, filtfilt, stft

import matplotlib.pyplot as plt
import seaborn as sns

file_path = "hyp le 5 sets set 2.txt"
fs = 1500
# step
# 1
df = pd.read_csv(file_path, delimiter='\t', skiprows=4)
df.rename(columns={
    'Time,s': 'time',
    'RT VLO,uV': 'vl',
    'RT RECTUS FEM.,uV': 'rf',
    'RT VMO,uV': 'vm'}, inplace=True)

df['time'] = pd.to_datetime(df['time'], unit='s')
df['rep'] = None
df = df.drop([column for column in df.columns if column.startswith('Mark')], axis=1)


def rolling_avg(df, window_size='200ms', columns=['vl', 'rf', 'vm']):
    window_size_int = int(pd.Timedelta(window_size).total_seconds() * fs)
    for column in columns:
        df[f'{column}_abs'] = df[column].abs()
        df[f'Rolling_average_{column}'] = df[f'{column}_abs'].rolling(window=window_size_int, min_periods=1,
                                                                      center=True).mean()
    return df


df = rolling_avg(df, window_size='200ms')

fig, axs = plt.subplots(nrows=3, sharex=True, sharey=False)


sns.lineplot(df, x=df.index, y='vl', ax=axs[0])
axs[0].set_title('Raw data', fontweight='bold', loc='right')
axs[0].get_yaxis().set_visible(False)
sns.lineplot(df, x=df.index, y='vl_abs', ax=axs[1], c='red')
axs[1].set_title('Rectification', fontweight='bold', loc='right')
axs[1].get_yaxis().set_visible(False)
sns.lineplot(df, x=df.index, y='Rolling_average_vl', ax=axs[2], c='green')
axs[2].set_title('Smoothing', fontweight='bold', loc='right')
axs[2].get_yaxis().set_visible(False)
[ax.set_ylabel('') for ax in axs]
[ax.set_xlabel('Time (s)') for ax in axs]


for ax in axs:
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['bottom'].set_visible(False)
    ax.spines['left'].set_visible(False)


plt.show()
    
plt.figure()
plt.plot(df['Rolling_average_vl'])
assert False
# df = df[df['Rolling_average_vl'] > 350]
# df[df['Rolling_average_vl'] < 90]=0
df = df.reset_index(drop=True)
plt.figure()
plt.plot(df['Rolling_average_vl'])
plt.figure()
sns.lineplot(data=df, x=df.index, y='vl_abs')


def _butter_bandpass(lowcut, highcut, fs, order=4):
    nyq = 0.5 * fs
    low = lowcut / nyq
    high = highcut / nyq
    b, a = butter(order, [low, high], btype='bandpass')
    return b, a


def butter_bandpass_filter(data, lowcut, highcut, fs, order=4):
    b, a = _butter_bandpass(lowcut, highcut, fs, order=order)
    filterd_data = filtfilt(b, a, data)

    # emg_rectified = abs(filterd_data)
    emg_envelope = filterd_data
    return emg_envelope


# step
# 4
df['filterd_vl'] = butter_bandpass_filter(df['vl'], 10, 500, fs)
plt.figure()
sns.lineplot(df, x=df.index, y='filterd_vl')

plt.figure()
# step
# 5
timewindow=0.3 #s
timeshift = 0.01#s
nperseg = timewindow*fs
noverlap = (timewindow-timeshift)*fs
f, t, Zxx = stft(df['filterd_vl'], fs, nperseg=nperseg, noverlap=noverlap) #noverlap gives the running average
# plt.pcolormesh(t, f, np.abs(Zxx), vmin=40, vmax=100, shading='gouraud')

plt.pcolormesh(t, f, np.abs(Zxx), vmin=20, vmax=100)
plt.title('STFT Magnitude')
plt.ylabel('Frequency [Hz]')
plt.xlabel('Time [sec]')
cbar = plt.colorbar(label='Magnitude')
# plt.pcolormesh(t, f, np.abs(Zxx), vmin=0, vmax=20)
# plt.title('STFT Magnitude')
# plt.ylabel('Frequency [Hz]')
# plt.xlabel('Time [sec]')
# cbar = plt.colorbar(label='Magnitude')

plt.figure()
for iter in range(len(t)):
    plt.plot(f, abs(Zxx[:,iter]))
    break

power_spectrum = np.abs(Zxx) ** 2
median_frequencies = np.zeros(len(t))
power = np.zeros(len(t))

for i, time_frame in enumerate(power_spectrum.T):  # Transpose power_spectrum to iterate over time frames
    # cumulative distribution function (CDF)
    cum_sum = np.cumsum(time_frame)
    power[i] = cum_sum[-1]
    cum_sum /= cum_sum[-1] 
    median_index = np.argmax(cum_sum >= 0.5)
    median_frequency = f[median_index]
    median_frequencies[i] = median_frequency

# step
# 7
# Create a DataFrame with time as x and median frequencies as y
data = {'Time': np.arange(0,len(median_frequencies)*timeshift, timeshift), 'Median Frequency': median_frequencies, 'Power': power/np.max(power)*100}
df = pd.DataFrame(data)

# Plot using lmplot
plt.figure()
# sns.lmplot(x='Time', y='Median Frequency', data=df, height=6, aspect=2)
# sns.lmplot(x='Time', y='Power', data=df, height=6, aspect=2)
sns.lmplot(x='Time', y='value', hue='variable',
             data=pd.melt(df, ['Time']), height=6, aspect=2)
plt.show()