import numpy as np


class GaussianFilter:
    def __init__(self, sigma):
        self.sigma = sigma
        self.kernel = self._create_kernel()

    def _create_kernel(self):
        x, y = np.mgrid[-self.sigma:self.sigma+1, -self.sigma:self.sigma+1]
        g = np.exp(-(x**2/float(self.sigma)+y**2/float(self.sigma)))
        return g / g.sum()

    def apply(self, input):
        """Apply Gaussian filter to the input image"""
        return np.convolve(input.flatten(), self.kernel.flatten(), mode='same').reshape(input.shape)

# 使用示例：
# gaussian_filter = GaussianFilter(sigma=1.5)
# filtered_image = gaussian_filter.apply(input_image)
