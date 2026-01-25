from vpython import *

g1 = graph(xtitle="v0 =[m/s]", ytitle = "max theta [deg]", width=500, height=250)
f1 = gcurve(color=color.red)

def prange(ttheta, v0, r0):
    g = vector(0,-9.8,0)
    m = 0.02
    R = 0.05
    rho = 1.2
    C = 0.47
    A = pi*R**2
    p = m*v0*vector(cos(ttheta), sin(ttheta), 0)
    t = 0 
    dt= 0.001
    r = r0

    while r.y >= 0:
        F = m*g -.5*rho*A*C*mag(p/m)**2*norm(p)
        p = p + F*dt
        r = r + p*dt/m
        t = t + dt
    return(r.x)
  
dtheta = .5*pi/180
vstart = 1
dv = 0.2

while vstart < 15:
    theta = 1*pi/180
    mrange = 0
    mangle = 0
    
    while theta < 89*pi/180:
        trange = prange(theta, vstart, vector(0,0,0))
        if trange > mrange:
            mrange = trange
            mangle = theta
        theta = theta + dtheta
    
    f1.plot(vstart, mangle*180/pi)
    vstart = vstart + dv
    rate(100)