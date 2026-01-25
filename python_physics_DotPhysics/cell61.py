from vpython import *
import time

g1 = graph(xtitle="t = [s]", ytitle="y = [m]", width=500, height=250)
f1 = gcurve(color=color.blue)

m =0.1
g = 9.8
y = 0.465
v = 0 

t = 0
dt = 0.01

k = 3.13
F0 = 2.65

while t < 4:
  F = -k*y + F0 - m*g
  a = F/m
  v = v + a*dt
  y = y + v*dt
  t = t+dt
  f1.plot(t,y)

Tobs = (10.53-8.2)/2
print("Tobs = ", Tobs, " s")

time.sleep(20)