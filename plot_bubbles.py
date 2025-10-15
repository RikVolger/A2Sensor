"""Load and process data from the A2 Fiber probe, turn into pretty graphs

Expects input to be .evt files from the M2 Analyzer for bubbly flows.
Requires adaptations in source code for changing source folders of the .evt files.

Outputs a figure for each data file, and a boxplot of the combined data.
Output folder is a new folder 'fig' in the source folder.
"""

import os
import csv
import numpy as np
import pandas as pd
from pathlib import Path
from matplotlib import pyplot as plt

inch = 2.54

# prefix and filename using Raw strings to get around \r being recognized as a special character
# using capital R for raw string because of failing syntax highlighting with small r in VSCode
prefix = Path(R"U:\Xray RPT ChemE\X-ray\Xray_data\2024-11-08 Rik en Sam - water scatter\Fiber Probe\241108 - Water center of column")

if not prefix.is_dir():
    print("Can't find source folder. Exiting.")
    quit()

filenames = []
flows = []

with open(prefix / "log.csv") as log_file:
    logreader = csv.DictReader(log_file, delimiter=',')
    for row in logreader:
        filenames.append(f"2024-11-08T{row['Timestamp']}.evt")
        flows.append(row["Flowrate (L/min)"])

fig_path = os.path.join(prefix, "fig")
os.makedirs(fig_path, exist_ok=True)

figtitles = [f"Water {flow} lmin" for flow in flows]

boxplot_labels = [f"{flow} L/min" for flow in flows]

i_fig = 0

all_data = []
all_data_log = []
d_32_all = []
median_all = []
mean_all = []

for filename, figtitle in zip(filenames, figtitles):
    df = pd.read_csv(prefix / filename, sep="\t", decimal=",")

    all_bubbles = df[["Number", "Valid", "Veloc", "Size", "Duration"]]

    # get fraction of 1 and 0 counts, convert to percentage
    all_bubbles.loc[all_bubbles.Size < 20, ["Valid"]] = 0
    validity = all_bubbles["Valid"].value_counts(normalize=True)
    validation_rate = validity.mul(100).astype(int).astype(str)[1]+"%"

    # extract specific data for valid and invalid events
    valid_bubbles_size = all_bubbles[["Number", "Size"]].loc[all_bubbles["Valid"] == 1]
    # valid_bubbles_size = valid_bubbles_size.loc[valid_bubbles_size["Size"] > 40]
    valid_bubbles_dur = all_bubbles[["Number", "Duration"]].loc[all_bubbles["Valid"] == 1]
    invalid_bubbles_dur = all_bubbles[["Number", "Duration"]].loc[all_bubbles["Valid"] == 0]
    Q1, Q3 = valid_bubbles_size['Size'].quantile([.25, .75])

    valid_bubbles_size["d3"] = valid_bubbles_size["Size"]**3
    valid_bubbles_size["d2"] = valid_bubbles_size["Size"]**2
    d_32 = valid_bubbles_size["d3"].sum() / valid_bubbles_size["d2"].sum()
    d_32_mean = d_32.mean()
    d_32_all.append(d_32_mean)

    median = np.median(valid_bubbles_size["Size"])
    median_all.append(median)

    mean = np.mean(valid_bubbles_size["Size"])
    mean_all.append(mean)

    # store data for use in boxplot
    all_data.append(valid_bubbles_size["Size"].to_numpy())
    all_data_log.append(np.log10(valid_bubbles_size["Size"]))

    # print info about this condition
    print("\n" + "-"*50)
    print(f"Results for {figtitle}:")
    print(f"Total events:\t{all_bubbles['Number'].size}")
    print(f"Valid events:\t{valid_bubbles_size['Size'].size}")
    print(f"Validation:\t{validation_rate}")
    print(f"Sauter size:\t{d_32_mean:.0f}")
    print(f"Mean size:\t{valid_bubbles_size['Size'].mean():.0f}")
    print(f"Standard deviation size:\t{valid_bubbles_size['Size'].std(ddof=0):.0f}")
    print(f"Interquartile range of size:\t{Q1:.0f} - {Q3:.0f}")
    print(f"Mean chord duration (all):\t{all_bubbles['Duration'].mul(1000).mean():.2f}")
    print(f"Mean chord duration (valid):\t{valid_bubbles_dur['Duration'].mul(1000).mean():.2f}")
    print(f"Mean chord duration (invalid):\t{invalid_bubbles_dur['Duration'].mul(1000).mean():.2f}")
    print("-"*50 + "\n")

    # create plots of bubble size and chord length distributions
    plt.figure(figsize=(16/inch, 5.5/inch))
    plt.subplot(1, 2, 1)
    plt.hist(valid_bubbles_size["Size"], bins=50, edgecolor='0.25', linewidth=0.7)
    plt.title("Bubble size distribution")
    plt.xlabel("Size ($\mu$m)")
    plt.subplot(1, 2, 2)
    plt.hist(
        [valid_bubbles_dur["Duration"].mul(1000), invalid_bubbles_dur["Duration"].mul(1000)],
        bins=20,
        histtype="barstacked",
        edgecolor='0.25',
        linewidth=0.7
    )
    plt.legend(["Valid", "Invalid"])
    plt.title("Chord duration distribution")
    plt.xlabel("Duration (ms)")
    plt.suptitle(f"{figtitle} - {validation_rate} valid")

    plt.tight_layout()

    # make valid filename out of figure title
    figsavetitle = figtitle.replace(' + ', '_').replace(' (', '_(').replace(' ', '-')

    plt.savefig(f"{prefix}\\fig\{i_fig}_{figsavetitle}.png", dpi=300)

    i_fig += 1

# boxplots of bubble size distributions in all conditions
plt.figure(figsize=(9/inch, 7/inch))
plt.boxplot(all_data_log, labels=boxplot_labels)
plt.title("Bubble size distributions")
plt.ylabel("$log_{10}$ Size ($\mu$m)")
plt.xticks(rotation=45)
plt.tight_layout()

plt.savefig(f"{prefix}\\fig\{i_fig}_boxplot_all_data_log.png", dpi=300)

i_fig += 1

plt.figure(figsize=(9/inch, 7/inch))
plt.boxplot(all_data, labels=boxplot_labels)
plt.title("Bubble size distributions")
plt.ylabel("Size ($\mu$m)")
plt.xticks(rotation=45)
plt.tight_layout()

plt.savefig(f"{prefix}\\fig\{i_fig}_boxplot_all_data.png", dpi=300)

i_fig += 1

# Figure of median bubble sizes
plt.figure(figsize=(9/inch, 7/inch))
plt.plot([float(f) for f in flows], median_all, 'x')
plt.title("Median bubble size")
plt.ylabel("Size ($\mu$m)")
# plt.xticks(rotation=45)
plt.tight_layout()

plt.savefig(f"{prefix}\\fig\{i_fig}_median_all_data.png", dpi=300)

i_fig += 1

# Figure of mean bubble sizes
plt.figure(figsize=(9/inch, 7/inch))
plt.plot([float(f) for f in flows], mean_all, 'x')
plt.title("Mean bubble size")
plt.ylabel("Size ($\mu$m)")
# plt.xticks(rotation=45)
plt.tight_layout()

plt.savefig(f"{prefix}\\fig\{i_fig}_mean_all_data.png", dpi=300)

i_fig += 1

plt.figure(figsize=(9/inch, 7/inch))
plt.plot(flows, d_32_all, "x")
plt.ylim(bottom=0)
plt.legend()
plt.title("Sauter mean diameter")
plt.xlabel("Flowrate (L/min)")
plt.ylabel("$d_{32}$ ($\mu$m)")
plt.xticks(rotation=45)
plt.tight_layout()

plt.savefig(f"{prefix}\\fig\{i_fig}_sauter_diameters.png", dpi=300)

plt.show()
