from pathlib import Path
import csv
import matplotlib.pyplot as plt
import numpy as np


header = []

def open_datafile(datafile):
    global header
    with open(datafile, 'rt') as f:
        reader = csv.reader(f, delimiter=' ', skipinitialspace=True)
        header = next(reader)
        rows, cols = next(reader)
        rows = int(rows)
        cols = int(cols)
        data = np.zeros((rows, cols))
        for idx, row in enumerate(reader):
            data[idx, :] = row
    return data


def compare_results(*mod_dirs, show=True):
    datafiles = [Path(f'recording/{mod}.dat') for mod in mod_dirs]
    mod_data = [open_datafile(mod) for mod in datafiles if mod.exists()]

    selected_locations = {x: header.index(x) for x in ('soma', 'ais5', 'node[0]')}

    plt.figure('Plot/Compare Results')
    plt.subplot(1, 2, 1)
    plt.xlabel('ms')
    plt.ylabel('mV')
    plt.title('Voltage Traces')
    for mod, data in zip(mod_dirs, mod_data):
        t = np.linspace(0, 100, data.shape[0])
        for column, idx in selected_locations.items():
            plt.plot(t, data[:, idx], label=f'{mod} {column}')
    plt.legend()

    plt.subplot(1, 2, 2)
    plt.title(f'Error Traces,\nreference mod-dir "{mod_dirs[0]}"')
    plt.xlabel('ms')
    plt.ylabel('|mV|')
    plt.axhline(0, color='k')
    ref_data = mod_data[0]
    ref_t    = np.linspace(0, 100, ref_data.shape[0])
    for mod, data in zip(mod_dirs[1:], mod_data[1:]):
        t = np.linspace(0, 100, data.shape[0])
        for column, idx in selected_locations.items():
            ref_interp = np.interp(t, ref_t, ref_data[:, idx])
            error = np.abs(ref_interp - data[:, idx])
            plt.plot(t, error, label=f'{mod} {column}')

    plt.legend()

    if show: plt.show()


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('mod', type=str, nargs='+')
    args = parser.parse_args()
    compare_results(*args.mod)

