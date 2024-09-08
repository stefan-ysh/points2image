import numpy as np


def gaussian_filter(input, sigma):
    """Simple Gaussian filter implementation using NumPy"""
    x, y = np.mgrid[-sigma:sigma+1, -sigma:sigma+1]
    g = np.exp(-(x**2/float(sigma)+y**2/float(sigma)))
    g = g / g.sum()
    return np.convolve(input.flatten(), g.flatten(), mode='same').reshape(input.shape)
