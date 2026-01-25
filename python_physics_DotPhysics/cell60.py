from vpython import *
import time
g1 = graph(xtitle = "r [m]", ytitle = "E [J]", width=500, height=250)
fK = gcurve(color=color.red, label = "kE", dot=True)
fU = gcurve(color=color.green, label = "U", dot=True)
fE = gcurve(color=color.blue, label = "E", dot=True)

G = 6.67e-11
ME = 5.97e24
RE = 6.37e6

earth = sphere(pos=vector(0,0,0), radius=RE, texture=textures.earth)
craft = sphere(pos=vector(2*RE,0,0), radius=RE/30, color=color.yellow, make_trail=True)

craft.m = 1000
craft.p = vector(0,6500,0)*craft.m

t = 0
dt = 10

while t <30000:
  rate(200)
  r = craft.pos - earth.pos
  F = -G*ME*craft.m*norm(r)/mag(r)**2
  craft.p = craft.p + F*dt
  craft.pos = craft.pos + craft.p*dt/craft.m
  t = t+dt
  K = mag(craft.p)**2 / (2*craft.m)
  U = -G*ME*craft.m/mag(r)
  E = K + U
  fK.plot(mag(r),K)
  fU.plot(mag(r),U)
  fE.plot(mag(r),E)

time.sleep(60)