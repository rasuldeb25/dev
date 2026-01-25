from vpython import *
import time

#defining a ball, sphere() is built-in fuction of vpython
#pos is vector location of an object
#make_trail = True is to show the trajectory of the ball
ball = sphere(pos=vector(0,.1,0), radius=0.05, color=color.yellow, make_trail = True)

#defining a ground, box() is also built-in funtion of vpython
#similar to ball here we are using size = to define the size of the box, while in ball we used radius=
ground = box(pos=vector(0,0,0), size = vector(2.5,0.02,0.15))

g1 = graph(xtitle="t [s]", ytitle="y [m]")
f1 = gcurve(color=color.blue)

#defining a gravatiotanal field
g = vector(0,-9.8,0)

#defining mass of the ball, we use .m here, we can just say m, but if there are more objects it is better to use .m
ball.m = 0.05

#defining initial velocity
v0=3.5
theta = 73*pi/180
ball.v = v0*vector(cos(theta),sin(theta),0)

vscale=.1
varrow = arrow(pos=ball.pos, axis=vscale*ball.v, color=color.cyan)

t = 0 
dt=0.01

#running the loop as long as the ball is physically above the ground height
#we check ball.pos.y against the ground position + radius to account for the ball's thickness
while ball.pos.y >= ground.pos.y + ball.radius + ground.size.y:
    
    #calculating the force of gravity on the ball
    F = ball.m*g
    
    #calculating acceleration using Newton's second law (a = F/m)
    a = F/ball.m
    
    #updating the velocity by adding the change in velocity (a*dt)
    ball.v = ball.v + a*dt
    
    #updating the position by adding the change in position (v*dt)
    ball.pos = ball.pos + ball.v*dt
    
    #updating the visual arrow to follow the ball's new position
    varrow.pos = ball.pos
    
    #updating the arrow's length/direction to match the new velocity vector
    varrow.axis = vscale*ball.v
    
    #incrementing the time step
    t = t + dt
    
    #rate(100) limits the loop to 100 calculations per second so animation is smooth
    rate(100)
    
    #plotting the current time and height on the graph
    f1.plot(t,ball.pos.y)

#pausing the program for 60 seconds after the loop finishes so the window doesn't close
time.sleep(60)