from vpython import *

g1 = graph(xtitle="x = [m]", ytitle = "y = [m]", width=500, height=250)
f1 = gcurve(color=color.cyan)
g = vector(0,-9.8,0)
r = vector(0,0,0)
theta = 30*pi/180
v0 = 8
m = 0.05
t = 0
dt= 0.01
p = m*v0*vector(cos(theta), sin(theta), 0)

while r.y >= 0:
  F = m*g
  p = p + F*dt
  r = r + p*dt/m
  t = t + dt
  f1.plot(r.x, r.y)