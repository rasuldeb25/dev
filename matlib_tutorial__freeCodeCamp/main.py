import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

gas = pd.read_csv("gas_prices.csv")
plt.figure(figsize=(8,5))

plt.title("Gas prices over time in USD")

for country in gas:
    if country != "Year":
        plt.plot(gas.Year, gas[country], marker=".", label=country)

plt.xticks(gas.Year[::3])
plt.xlabel("Year")
plt.ylabel("US Dollars")

plt.legend()

plt.show()