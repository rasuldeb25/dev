from vpython import *

g1 = graph(title="kinematics", xtitle="time[s]", ytitle="x[m]",
width=500, height=200, fast=False)
f1 = gcurve(color=color.cyan, markers=True)
x = 0
v = 0.45
t = 0
dt = .01
a = -0.002

print("Starting simulation...")

while t < 1.5:
    rate(50) 
    v = v + a*dt
    x = x + v*dt
    t = t + dt
    f1.plot(t, x)