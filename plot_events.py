import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import xml.etree.ElementTree as ET
from extract_binary_values import readBinFileAndConvertToVoltage


# load evt file (recognized air-events)
def conv(val):
    try:
        return float(val)
    except ValueError:
        return float(val.replace(b',', b'.'))


# load log file
def get_acquisition_parameters(file):
    evtlog = ET.parse(file)
    root = evtlog.getroot()
    f = float(root[0].attrib['acquisitionFrequency'])
    coef1 = float(root[0][2].attrib['channelCoef1'])
    coef2 = float(root[0][2].attrib['channelCoef2'])
    return f, coef1, coef2


def build_title(evt):
    title = ''
    if evt['Valid']:
        title += 'Valid bubble'
    else:
        title += 'Invalid bubble'
    title += '; '
    if evt['OKIn']:
        title += 'Valid entry'
    else:
        title += 'Invalid entry'
    title += '; '
    if evt['OKOut']:
        title += 'Valid exit'
    else:
        title += 'Invalid exit'
    return title

if __name__ == "__main__":
    file_root = R"C:\Users\rikvolger\Documents\Codebase\A2Sensor\data\binaries\2024-03-27T092058" 
    evt_file = file_root + ".evt"
    events = pd.read_csv(evt_file, sep="\t", header=0, decimal=",")

    acq_frequency, coef1, coef2 = get_acquisition_parameters(file_root + ".evtlog")

    bin_file = file_root + ".bin"
    bin_data = readBinFileAndConvertToVoltage(bin_file, coef1, coef2)

    # read coeffs and frequency
    # for each event
    # for i, evt in events.iterrows():
    for i, evt in events.reindex().sort_index(ascending=False).iterrows():
        # read corresponding part of voltage data
        evt_data = bin_data.get_range(int(evt['Start']), int(evt['End']))
        evt_times = [(i + int(evt['Start'])) / acq_frequency / 60 for i in range(len(evt_data))]
        entry_time = evt['Entry'] / acq_frequency / 60
        exit_time = evt['Exit'] / acq_frequency / 60
        title = build_title(evt)
        # titlestring: (in)valid bubble; (in)valid start; (in)valid end
        # create plot of data
        fig, ax = plt.subplots(1, 1)
        ax.plot(evt_times, evt_data)
        ax.plot([entry_time, entry_time], [0, max(evt_data)])
        ax.plot([exit_time, exit_time], [0, max(evt_data)])
        ax.set_xlabel("Time (minutes)")
        ax.set_ylabel("Signal (V)")
        ax.set_title(title)
        # show plot
        plt.show()

    for i, evt in events.iterrows():
        if evt['OKOut']:
            print(evt['OKIn'])
        if evt['OKIn'] and evt['OKOut']:
            print(evt['VeloIn'], evt['VeloOut'])
