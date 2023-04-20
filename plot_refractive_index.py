
from matplotlib import pyplot as plt
import pandas as pd

inch = 2.54

ri = pd.read_csv(R"C:\Users\rikvolger\OneDrive - Delft University of Technology\Experimental\A2 Fiber Probe\refrective-index-ethanol-water.csv", delimiter=";")

plt.figure(figsize=(8/inch, 5.5/inch))
plt.plot(ri["Percent water"], ri["Refractive index"])
plt.grid(visible=True)
plt.ylim((1.3, 1.4))
plt.ylabel("Refractive index")
plt.xlabel("Percentage water")
plt.title("Refractive index of\nwater-ethanol mixtures")
plt.tight_layout()
plt.savefig(R"C:\Users\rikvolger\OneDrive - Delft University of Technology\Experimental\A2 Fiber Probe\Refractive index of water-ethanol mixtures.png", dpi=300)
plt.show()