from vpython import *
import time

g1 = graph(xtitle="t[s]", ytitle="x[m]", width=500, height =250)
f1 = gcurve(color=color.red)
m = 0.1
k = 5000.5
g = vector(0,-9.8,0)
L0 = 0.15
theta = 60*pi/180

top = sphere(pos = vector(0,L0,0), radius=0.004)
mass = sphere(pos = top.pos + L0*vector(-sin(theta), -cos(theta), 0 ), radius=0.01,
              color=color.yellow, make_trail=True)
spring = helix(pos=top.pos, axis=mass.pos-top.pos, radius=0.005, 
              color=color.cyan, thickness=0.003)
              
mass.p = m*vector(0,0,0)
t = 0
dt = 0.001

while t < 5.5:
  rate(1000)
  L = mass.pos - top.pos
  spring.axis = L
  #mag() is built-in function of Python, returns the magnitude of the vector
  #norm() is built-in fucntion of VPython, returns a unit vector in the same direction
  F = -k*(mag(L)-L0)*norm(L) + m*g
  mass.p = mass.p + F*dt
  mass.pos = mass.pos+mass.p*dt/m
  t = t+dt
  
  f1.plot(t,mass.pos.x)
Tt = 2*pi*sqrt(L0/mag(g))
print("T theory = ", Tt)

time.sleep(60)