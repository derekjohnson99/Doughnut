#!/usr/bin/env python3
# coding: utf-8
'''
donut.c translated into python
'''

import time
import numpy as np
from numpy import sin, cos, pi
from numba import jit

# Create a circle of radius R1 centered at R2
# Create a doughnut by rotating about the Y axis
# Spin the doughnut around the X and Z axis
# Project doughnut onto 2D screen
# Determine illumination by calculating surface normal (given light source)

SCREEN_WIDTH = 80
SCREEN_HEIGHT = 28

ZBUFFER_BASE = np.zeros((SCREEN_HEIGHT, SCREEN_WIDTH), dtype=np.float32)
FRAME_BASE = np.full((SCREEN_HEIGHT, SCREEN_WIDTH), ord(' '), dtype=np.ubyte)

def draw_doughnut():

    A = 0
    B = 0

    while True:
        #print("\n")
        start = time.perf_counter()
        frame = render_frame(A, B)
        end = time.perf_counter()
        render_time = f"Render time = {end-start:1.4f} s"
        for i, letter in enumerate(render_time):
            frame[SCREEN_HEIGHT - 1, i] = ord(letter)
        for line in frame:
            print(str(line, 'utf-8'))
        A += 0.04
        B += 0.02
        time.sleep(0.015)
        print(f"\x1b[{SCREEN_HEIGHT + 1}A")

@jit(nopython=True)
def render_frame(A, B):
    theta_steps = 90
    phi_steps = 314
    R1 = 1.15
    R2 = 2
    K2 = 5

    # Calculate K1 based on screen size: the maximum x-distance occurs
    # roughly at the edge of the torus, which is at x=R1+R2, z=0.  we
    # want that to be displaced 3/8ths of the width of the screen, which
    # is 3/4th of the way from the center to the side of the screen.
    # SCREEN_WIDTH*3/8 = K1*(R1+R2)/(K2+0)
    #K1 = SCREEN_WIDTH*K2*3/(8*(R1+R2))
    #K1 = SCREEN_HEIGHT*K2*3/(8*(R1+R2));
    K1 = 19

    cosA = cos(A)
    sinA = sin(A)
    cosB = cos(B)
    sinB = sin(B)

    zbuffer = ZBUFFER_BASE.copy()
    frame = FRAME_BASE.copy()

    for i in range(theta_steps):
        theta = i * 2 * pi / theta_steps
        # precompute sines and cosines of theta
        cosT = cos(theta)
        sinT = sin(theta)

        for j in range(phi_steps):
            phi = j * 2 * pi / phi_steps
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
            xp = int(SCREEN_WIDTH / 2 + int(K1 * ooz * x))
            yp = int(SCREEN_HEIGHT / 2 - int(K1 * ooz * y))

            # calculate luminance.  ugly, but correct.
            L = cosP*cosT*sinB - cosA*cosT*sinP - sinA*sinT + cosB * (cosA*sinT - cosT*sinA*sinP)
            # L ranges from -sqrt(2) to +sqrt(2).  If it's < 0, the surface
            # is pointing away from us, so we won't bother trying to plot it.
            if L > 0 and 0 <= xp < SCREEN_WIDTH and 0 <= yp < SCREEN_HEIGHT:
                # test against the z-buffer.  larger 1/z means the pixel is
                # closer to the viewer than what's already plotted.
                if ooz > zbuffer[yp, xp]:
                    zbuffer[yp, xp] = ooz
                    luminance_index = int(L*8)
                    # luminance_index is now in the range 0..11 (8*sqrt(2) = 11.3)
                    # now we lookup the character corresponding to the
                    # luminance and plot it in our output:
                    frame[yp, xp] = ord(".,-~:;=!*#$@"[luminance_index])

    return frame

if __name__ == "__main__":

    draw_doughnut()
