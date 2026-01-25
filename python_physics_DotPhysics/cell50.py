from vpython import *

my_graph = graph(title="Position vs Time", xtitle="Time (s)", ytitle="Position (m)")
f1 = gcurve(color=color.cyan)

x = 0
v = 0.45
t = 0
dt = 0.025
a = -0.002

print("Starting simulation...")

while t < 1.5:
    rate(50) 
    v = v + a*dt
    x = x + v*dt
    t = t + dt
    f1.plot(t, x)