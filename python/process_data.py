import pandas as pd
import matplotlib.pyplot as plt

DATA_FILE = 'sensor_data.csv'


def load_data(path=DATA_FILE):
    cols = ['timestamp_ms', 'ecg', 'ir', 'red']
    return pd.read_csv(path, names=cols)


def plot_data(df):
    fig, ax = plt.subplots(3, 1, sharex=True)
    ax[0].plot(df['timestamp_ms'], df['ecg'], label='ECG')
    ax[0].set_ylabel('ECG')
    ax[1].plot(df['timestamp_ms'], df['ir'], label='IR', color='r')
    ax[1].set_ylabel('IR')
    ax[2].plot(df['timestamp_ms'], df['red'], label='RED', color='m')
    ax[2].set_ylabel('RED')
    ax[2].set_xlabel('Time (ms)')
    plt.show()


def main():
    df = load_data()
    print(df.head())
    plot_data(df)


if __name__ == '__main__':
    main()
