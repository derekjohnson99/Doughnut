#!/usr/bin/env python3
# coding: utf-8
'''
donut.c translated into python
'''

from math import sin, cos
import sys
import time
import numpy as np

# Create a circle of radius R1 centered at R2
# Create a doughnut by rotating about the Y axis
# Spin the doughnut around the X and Z axis
# Project doughnut onto 2D screen
# Determine illumination by calculating surface normal (given light source)

def draw_doughnut():

    A = 0
    B = 0

    while True:
        print("\x1b[23A")
        #print("\n")
        render_frame(A, B)
        A += 0.04
        B += 0.02
        #time.sleep(0.015)

def render_frame(A, B):
    theta_spacing = 0.07
    phi_spacing = 0.02
    R1 = 1
    R2 = 2
    K2 = 5

    screen_width = 80
    screen_height = 22

    # Calculate K1 based on screen size: the maximum x-distance occurs
    # roughly at the edge of the torus, which is at x=R1+R2, z=0.  we
    # want that to be displaced 3/8ths of the width of the screen, which
    # is 3/4th of the way from the center to the side of the screen.
    # screen_width*3/8 = K1*(R1+R2)/(K2+0)
    # screen_width*K2*3/(8*(R1+R2)) = K1
    K1 = screen_height*K2*3/(8*(R1+R2));

    cosA = cos(A)
    sinA = sin(A)
    cosB = cos(B)
    sinB = sin(B)

    zbuffer = [0.0] * 1760
    output = [' '] * 1760

    for i in range(90):
        theta = i * theta_spacing
        # precompute sines and cosines of theta
        cosT = cos(theta)
        sinT = sin(theta)

        for j in range(314):
            phi = j * phi_spacing
            # precompute sines and cosines of phi
            cosP = cos(phi)
            sinP = sin(phi)

            # the x,y coordinate of the circle, before revolving (factored
            # out of the above equations)
            circlex = R2 + R1 * cosT
            circley = R1 * sinT

            # final 3D (x,y,z) coordinate after rotations, directly from
            # our math above
            x = circlex * (cosB * cosP + sinA * sinB * sinP) - circley * cosA * sinB
            y = circlex * (sinB * cosP - sinA * cosB * sinP) + circley * cosA * cosB
            z = K2 + cosA * circlex * sinP + circley * sinA
            ooz = 1/z  # "one over z"

            # x and y projection.  note that y is negated here, because y
            # goes up in 3D space but down on 2D displays.
            xp = int(screen_width / 2 + int(K1 * ooz * x))
            yp = int(screen_height / 2 - int(K1 * ooz * y))

            buf_idx = xp + screen_width * yp
            assert buf_idx < 1760

            # calculate luminance.  ugly, but correct.
            L = cosP*cosT*sinB - cosA*cosT*sinP - sinA*sinT + cosB * (cosA*sinT - cosT*sinA*sinP)
            # L ranges from -sqrt(2) to +sqrt(2).  If it's < 0, the surface
            # is pointing away from us, so we won't bother trying to plot it.
            if (L > 0):
                # test against the z-buffer.  larger 1/z means the pixel is
                # closer to the viewer than what's already plotted.
                if (ooz > zbuffer[buf_idx]):
                    zbuffer[buf_idx] = ooz
                    luminance_index = int(L*8)
                    # luminance_index is now in the range 0..11 (8*sqrt(2) = 11.3)
                    # now we lookup the character corresponding to the
                    # luminance and plot it in our output:
                    output[buf_idx] = ".,-~:;=!*#$@"[luminance_index]

    for c in range(1760):
        sys.stdout.write(output[c])
        if c % screen_width == screen_width - 1:
            sys.stdout.write('\n')
        sys.stdout.flush()

if __name__ == "__main__":

    draw_doughnut()
