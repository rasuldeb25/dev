
from vpython import *
import time

g1 = graph(title="kinematics", xtitle="time[s]", ytitle="x[m]",
width=500, height=250, fast=True)
fA = gcurve(color=color.cyan, markers=False, label="Car A")
fB = gcurve(color=color.red, markers=False, label="Car B")
xA = 0.5
xB = 0
vA = 0.45
vB = 0
t = 0
dt = .01
aA = 0
aB = 0.2


while xA > xB:
    vA = vA + aA*dt
    vB = vB + aB*dt
    xA = xA + vA*dt
    xB = xB + vB*dt
    t = t + dt
    fA.plot(t, xA)
    fB.plot(t,xB)
print("xA = xB = ", xA, " m")
print("t= ", t, " s")
