from vpython import *
import time

ball = sphere(pos =vector(-2,.1,0), radius=0.05, color=color.yellow, make_trail = True)
ground = box(pos=vector(0,0,0), size = vector(4.5,0.02,0.15))
g1 = graph(xtitle="t [s]", ytitle="y [m]")
f1 = gcurve(color=color.blue)
g = vector(0,-9.8,0)
ball.m = 0.05
v0=7.2
theta = 73*pi/180
ball.p = ball.m*v0*vector(cos(theta),sin(theta),0)
vscale=.1
#varrow = arrow(pos=ball.pos, axis=vscale*ball.v, color=color.cyan)
ball2 = sphere(pos=ball.pos, radius=ball.radius, color=color.cyan, make_trail=True)
ball2.m=0.05
ball2.p= ball2.m*v0*vector(cos(theta),sin(theta),0)
rho = 1.2
A = pi*ball2.radius**2
C = 0.47

t = 0 
dt=0.01

while ball.pos.y>=ground.pos.y+ball.radius+ground.size.y:
  F = ball.m*g
  F2 = ball2.m*g - .5*rho*A*C*mag(ball2.p)**2*norm(ball2.p)/ball2.m**2
  
  ball.p = ball.p + F*dt
  ball2.p =ball2.p +F2*dt
  ball.pos = ball.pos + ball.p*dt/ball.m
  ball2.pos = ball2.pos +ball2.p*dt/ball2.m
  t = t + dt
  rate(100)
  f1.plot(t,ball.pos.y)
time.sleep(60)