##########################################################
# Problem 1: Car A starts at x=0.5m with a velocity of   #
# 0.45m/s. Car B starts at x=0 with a velocity of        # 
# 0m/s but has an acceleration of a = 0.2m/s^2.          #
# When does the Car B catch up to Car A?                 #
# Where do they meet?                                    #
# ######################################################## 

from vpython import *
import time

g1 = graph(title="kinematics", xtitle="time[s]", ytitle="x[m]",
width=500, height=250, fast=True)

fA = gcurve(color=color.cyan, markers=False, label="Car A")
fB = gcurve(color=color.red, markers=False, label="Car B")
xA = 0.5
xB = 0
vA = 0.45
vB = 0
t = 0
dt = .01
aA = 0
aB = 0.2


while t < 10.5:
    vA = vA + aA*dt
    vB = vB + aB*dt
    xA = xA + vA*dt
    xB = xB + vB*dt
    t = t + dt
    rate(100)
    fA.plot(t, xA)
    fB.plot(t,xB)

time.sleep(20)