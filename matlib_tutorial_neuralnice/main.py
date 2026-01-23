import matplotlib.pyplot as plt
import numpy as np
from matplotlib import style
import random

heads_tails = [0,0]

for _ in range(50): #->#dont run this in juypternotebook with big values RANGEs
    heads_tails[random.randint(0,1)] +=1
    plt.bar(["Heads", "Tails"], heads_tails, color=["red", "blue"])
    plt.pause(0.001)
plt.show() 