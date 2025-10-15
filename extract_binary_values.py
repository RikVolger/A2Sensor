import numpy as np


def readBinFileAndConvertToVoltage(file_path: str, coef1: float, coef2: float):
    """Read a binary file of fiber probe data and output np array of voltage

    Args:
        file_path (str): Path to binary file (file or Pathlib.Path also work)
        coef1 (float): Voltage offset (field channelCoef1 in .binlog file)
        coef2 (float): Voltage range (field channelCoef2 in .binlog file)

    Returns:
        np.ndarray: All voltage values found in binary
    """
    voltData = VoltageData(
        np.fromfile(file_path, np.dtype('>i2')),
        coef1,
        coef2)
    return voltData


class VoltageData():
    def __init__(self, data, coef1, coef2):
        self.data = data
        self.coef1 = coef1
        self.coef2 = coef2

    def get_range(self, start, stop):
        return self.data[start:stop] * self.coef2 + self.coef1


if __name__ == "__main__":
    fpath = R"C:\Users\rikvolger\Documents\Codebase\A2Sensor\data\binaries\2024-03-27T092058.bin"
    coef1 = 0.0
    coef2 = 6.1037018951994385e-05

    data = readBinFileAndConvertToVoltage(fpath, coef1, coef2)

    print(data.get_range(0, 10))
