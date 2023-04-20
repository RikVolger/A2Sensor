import os
import numpy as np
import pandas as pd
from matplotlib import pyplot as plt

inch = 2.54

# prefix and filename using Raw strings to get around \r being recognized as a special character
# using capital R for raw string because of failing syntax highlighting with small r
prefix = R"C:\Users\rikvolger\OneDrive - Delft University of Technology\Experimental\A2 Fiber Probe\23-01-12 Tryout"
filenames = [
    R"\2023-01-12T145535.evt",
    R"\2023-01-12T151513.evt",
    R"\2023-01-12T154712.evt",
    R"\2023-01-12T160208.evt",
]

fig_path = os.path.join(prefix, "fig")
os.makedirs(fig_path, exist_ok=True)

figtitles = [
    "Water",
    "Water (accelerated)",
    "Water + EtOH 1% (accelerated)",
    "Water + EtOH 3% (accelerated)",
]

boxplot_labels = ["W", "W(a)", "WE1(a)", "WE3(a)"]

i_fig = 0

all_data = []
all_data_log = []

for filename, figtitle in zip(filenames, figtitles):
    df = pd.read_csv(prefix+filename, sep="\t", decimal=",")

    all_bubbles = df[["Number", "Valid", "Veloc", "Size", "Duration"]]
    
    # get fraction of 1 and 0 counts, convert to percentage
    validity = all_bubbles["Valid"].value_counts(normalize=True)
    validation_rate = validity.mul(100).astype(int).astype(str)[1]+"%"

    # extract specific data for valid and invalid events
    valid_bubbles_size = all_bubbles[["Number", "Size"]].loc[df["Valid"] == 1]
    valid_bubbles_dur = all_bubbles[["Number", "Duration"]].loc[df["Valid"] == 1]
    invalid_bubbles_dur = all_bubbles[["Number", "Duration"]].loc[df["Valid"] == 0]
    Q1, Q3 = valid_bubbles_size['Size'].quantile([.25, .75])
    
    # store data for use in boxplot
    all_data.append(valid_bubbles_size["Size"].to_numpy())
    all_data_log.append(np.log10(valid_bubbles_size["Size"]))

    # print info about this condition
    print("\n" + "-"*50)
    print(f"Results for {figtitle}:")
    print(f"Total events:\t{all_bubbles['Number'].size}")
    print(f"Valid events:\t{valid_bubbles_size['Size'].size}")
    print(f"Validation:\t{validation_rate}")
    print(f"Mean size:\t{valid_bubbles_size['Size'].mean()}")
    print(f"Standard deviation size:\t{valid_bubbles_size['Size'].std(ddof=0)}")
    print(f"Interquartile range of size:\t{Q1:.0f} - {Q3:.0f}")
    print(f"Mean chord duration (all):\t{all_bubbles['Duration'].mul(1000).mean()}")
    print(f"Mean chord duration (valid):\t{valid_bubbles_dur['Duration'].mul(1000).mean()}")
    print(f"Mean chord duration (invalid):\t{invalid_bubbles_dur['Duration'].mul(1000).mean()}")
    print("-"*50 + "\n")

    # create plots of bubble size and chord length distributions
    plt.figure(figsize=(16/inch, 5.5/inch))
    plt.subplot(1, 2, 1)
    plt.hist(valid_bubbles_size["Size"], bins=20, edgecolor='0.25', linewidth=0.7)
    plt.title("Bubble size distribution")
    plt.xlabel("Size ($\mu$m)")
    plt.subplot(1, 2, 2)
    plt.hist([valid_bubbles_dur["Duration"].mul(1000), invalid_bubbles_dur["Duration"].mul(1000)], bins=20, histtype="barstacked", edgecolor='0.25', linewidth=0.7)
    plt.legend(["Valid", "Invalid"])
    plt.title("Chord duration distribution")
    plt.xlabel("Duration (ms)")
    plt.suptitle(f"{figtitle} - {validation_rate} valid")

    plt.tight_layout()

    plt.savefig(f"{prefix}\\fig\{i_fig}_{figtitle.replace(' + ', '_').replace(' (', '_(')}.png", dpi=300)
    
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

# plt.show()