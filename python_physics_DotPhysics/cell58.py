from vpython import *

g1 = graph(xtitle="theta = [deg]", ytitle = "range = [m]", width=500, height=250)
f1 = gcurve(color=color.cyan)

def prange(ttheta, v0, r0):
  g = vector(0,-9.8,0)
  m = 0.05
  p = m*v0*vector(cos(ttheta), sin(ttheta), 0)
  t = 0
  dt= 0.01
  r = r0

  while r.y >= 0:
    F = m*g
    p = p + F*dt
    r = r + p*dt/m
    t = t + dt
  return(r.x)
  
theta = 1*pi/180
dtheta = 1*pi/180
vstart = 7


while theta<89*pi/180:
  trange = prange(theta, vstart, vector(0,0,0))
  f1.plot(theta*180/pi,trange)
  theta = theta + dtheta