import numpy as np
import cv2
import dtcwt

class DtcwtImgDecoder:

    def __init__(self, key=None, str=1.0, step=5.0, blk_shape=(35, 30)):
        self.key = key
        self.alpha = default_scale * str
        self.step = step
        self.blk_shape = blk_shape

    def decode(self, yuv):
        wmed_transform = dtcwt.Transform2d()
        wmed_coeffs = wmed_transform.forward(yuv[:, :, 1], nlevels=3)
        y_transform = dtcwt.Transform2d()
        y_coeffs = y_transform.forward(yuv[:, :, 0], nlevels=3)

        masks3 = [0 for i in range(6)]
        inv_masks3 = [0 for i in range(6)]
        shape3 = y_coeffs.highpasses[2][:, :, 0].shape
        for i in range(6):
            masks3[i] = cv2.filter2D(np.abs(y_coeffs.highpasses[1][:,:,i]), -1, np.array([[1/4, 1/4], [1/4, 1/4]]))
            masks3[i] = np.ceil(rebin(masks3[i], shape3) * (1.0 / self.step))
            masks3[i][masks3[i] == 0] = 0.01
            masks3[i] *= 1.0 / max(12.0, np.amax(masks3[i]))
            inv_masks3[i] = 1.0 / masks3[i]

        shape = wmed_coeffs.highpasses[2][:,:,i].shape
        h, w = (shape[0] + 1) // 2, (shape[1] + 1) // 2
        coeffs = np.zeros((h, w, 6), dtype='complex_')
        for i in range(6):
            coeff = (wmed_coeffs.highpasses[2][:,:,i]) * inv_masks3[i] * 1 / self.alpha
            coeffs[:,:,i] = coeff[:h, :w] + coeff[:h, -w:] + coeff[-h:, :w] + coeff[-h:, -w:]
        highpasses = tuple([coeffs])
        lowpass = np.zeros((h * 2, w * 2))
        t = dtcwt.Transform2d()
        wm = t.inverse(dtcwt.Pyramid(lowpass, highpasses))

        return wm