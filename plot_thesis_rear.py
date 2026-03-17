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


def build_title(i, evt):
    title = f'{i:03d}; '
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
    file_root = R"C:\Users\rikvolger\Codebase\A2Sensor\data\binaries\2024-03-27T092058" 
    evt_file = file_root + ".evt"
    events = pd.read_csv(evt_file, sep="\t", header=0, decimal=",")

    indices = [4684, 4667, 4650, 4616, 4581, 4564]

    acq_frequency, coef1, coef2 = get_acquisition_parameters(file_root + ".evtlog")

    bin_file = file_root + ".bin"
    bin_data = readBinFileAndConvertToVoltage(bin_file, coef1, coef2)

    # read coeffs and frequency
    # for each event
    # for i, evt in events.iterrows():
    # for i, evt in events.reindex().sort_index(ascending=False).iterrows():
    events.reindex().sort_index(ascending=False)
    
    i = 4667 
    # i = 4616 
    # i = 4581 
    # i = 4564
    i_back = 500
    i_forward = 20
    evt = events.iloc[i]
    # read corresponding part of voltage data
    if evt['Valid']:
        evt_data = bin_data.get_range(int(evt['Start']), int(evt['End']))
        evt_data = np.convolve(evt_data, [0.5, 0.5], 'valid')
        evt_times = int(evt['Start']) + np.arange(len(evt_data))
        exit_time = int(evt['Exit'])

        time_mask = ((evt_times > exit_time - i_back) &
                     (evt_times < exit_time + i_forward))

        title = build_title(i, evt)
        # titlestring: (in)valid bubble; (in)valid start; (in)valid end
        # create plot of data
        fig, ax = plt.subplots(1, 1)
        ax.plot(evt_times[time_mask], evt_data[time_mask])
        # ax.plot([exit_time, exit_time], [0, max(evt_data)])
        ax.axis('off')

        fig.savefig('C:\\Users\\rikvolger\\LaTeX Writing\\Thesis\\_figures\\png\\rear.png', dpi=900)
        # show plot
        plt.show()
