from vpython import *
import time
m = 0.1
k = 10.5
g = vector(0,-9.8,0)
L0 = 0.07

top = sphere(pos = vector(0,L0,0), radius=0.004)
mass = sphere(pos = top.pos - vector(.3*L0,L0,0), radius=0.01,
              color=color.yellow, make_trail=True)
spring = helix(pos=top.pos, axis=mass.pos-top.pos, radius=0.005, 
              color=color.cyan, thickness=0.003)
              
mass.p = m*vector(0.5,0,0.7)
t = 0
dt = 0.01

while t < 60:
  rate(100)
  L = mass.pos - top.pos
  spring.axis = L
  #mag() is built-in function of Python, returns the magnitude of the vector
  #norm() is built-in fucntion of VPython, returns a unit vector in the same direction
  F = -k*(mag(L)-L0)*norm(L) + m*g
  mass.p = mass.p + F*dt
  mass.pos = mass.pos+mass.p*dt/m
  t = t+dt
  
time.sleep(65)