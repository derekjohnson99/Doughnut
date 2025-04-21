#!/usr/bin/env python3
# coding: utf-8

import numpy as np
from numpy import sin, cos, pi
from numba import jit, njit, vectorize

SCREEN_WIDTH = 80
SCREEN_HEIGHT = 28

ZBUFFER_BASE = np.zeros((SCREEN_HEIGHT, SCREEN_WIDTH), dtype=np.float32)
FRAME_BASE = np.full((SCREEN_HEIGHT, SCREEN_WIDTH), ord(' '), dtype=np.ubyte)

@njit
def circ_rot(theta):
    "Point on circle centred at (R2, 0, 0), with radius R1 and theta radians from horizontal"
    R1 = 1.15
    R2 = 2
    return np.array([R2 + R1 * cos(theta), R1 * sin(theta), 0], np.float32)

#@njit
def Y(phi: np.float32) -> np.array:
    "Rotate phi radians around the y-axis"
    return np.array([[cos(phi), 0, sin(phi)], [0, 1, 0], [-sin(phi), 0, cos(phi)]], np.float32)

def X(A):
    "Rotate A radians around the x-axis"
    return np.array([[1, 0, 0], [0, cos(A), sin(A)], [0, -sin(A), cos(A)]], np.float32)

def Z(B):
    "Rotate B radians around the z-axis"
    return np.array([[cos(B), sin(B), 0], [-sin(B), cos(B), 0], [0, 0, 1]], np.float32)

def doughnut_surface_point(A, B, phi, theta):
    return circ_rot(theta) @ Y(phi) @ X(A) @ Z(B)

def surface_normal(A, B, phi, theta):
    return np.array([cos(theta), sin(theta), 0], np.float32) @ Y(phi) @ X(A) @ Z(B)

@njit
def screen_coords(point):
    K1 = 20
    K2 = 5 # Screen to origin z distance
    (x, y, z) = point
    return np.array([((K1 * x) / (K2 + z)), ((K1 * y) / (K2 + z))], np.float32)

def render_frame(A, B):
    zbuffer = ZBUFFER_BASE.copy()
    frame = FRAME_BASE.copy()
    for T in range(314):
        theta = T * 2 * pi / 314
        for P in range(90):
            phi = P * 2 * pi / 90
            surface_point = doughnut_surface_point(A, B, phi, theta)
            sc = screen_coords(surface_point)
            xp  =int(SCREEN_WIDTH / 2 + int(sc[0]))
            yp = int(SCREEN_HEIGHT / 2 - int(sc[1]))
            z = surface_point[2]

            L = surface_normal(A, B, phi, theta) @ np.array([0, 1, -1], np.float32)

            if L > 0 and 0 <= xp < SCREEN_WIDTH and 0 <= yp < SCREEN_HEIGHT:
                if z > zbuffer[yp, xp]:
                    zbuffer[yp, xp] = z
                    luminance_index = int(L*8)
                    frame[yp, xp] = ord(".,-~:;=!*#$@"[luminance_index])
    return frame

def spin_doughnut():
    A = 0
    B = 0
    while True:
        frame = render_frame(A, B)
        for line in frame:
            print(str(line, 'utf-8'))
        print(f"\x1b[{SCREEN_HEIGHT + 1}A")
        A += 0.04
        B += 0.02

if __name__ == "__main__":
    spin_doughnut()
