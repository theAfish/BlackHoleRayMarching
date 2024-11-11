import taichi as ti
import numpy as np
from gr_ray_tracing_model import Camera, PI

ti.init(arch=ti.gpu)

# Canvas
aspect_ratio = 16/9
image_width = 800
image_height = int(image_width / aspect_ratio)
canvas = ti.Vector.field(3, dtype=ti.f32, shape=(image_width, image_height))
bloom_img = ti.Vector.field(3, dtype=ti.f32, shape=(image_width, image_height))

# Rendering parameters
samples_per_pixel = 4
kernel_size = 11
sigma = int((kernel_size - 1) / 2)
gauss_mat = ti.field(dtype=ti.f32, shape=(kernel_size, kernel_size))


@ti.kernel
def init_gauss():
    sum = 0.0
    for i, j in ti.ndrange(kernel_size, kernel_size):
        i_ = i - sigma
        j_ = j - sigma
        gauss_mat[i, j] = 1/(2 * PI * sigma**2) * ti.exp(-(i_**2 + j_**2)/(2*sigma**2))
        sum += gauss_mat[i, j]
    for i, j in ti.ndrange(kernel_size, kernel_size):
        gauss_mat[i, j] /= sum

@ti.kernel
def render():
    for i, j in canvas:
        color = ti.Vector([0.0, 0.0, 0.0])
        for n in range(samples_per_pixel): # 采样四次
            u = (i + ti.random()) / image_width
            v = (j + ti.random()) / image_height
            ray = camera.get_ray(u, v)
            color += ray.update_euler() # 求和
        color /= samples_per_pixel # 取平均
        canvas[i, j] += color #　直接赋值
    for i, j in canvas:
        bloom_img[i, j] = kernel(i, j, canvas) * 0.2
    for i, j in canvas:
        bloom_img[i, j] += canvas[i, j] * 0.8

@ti.kernel
def bloom():
    for i, j in canvas:
        bloom_img[i, j] = kernel(i, j, canvas)

@ti.func
def kernel(x, y, img):
    out = ti.Vector([0.0, 0.0, 0.0])
    for i, j in ti.static(ti.ndrange(kernel_size, kernel_size)):
        out += gauss_mat[i, j] * img[x+i-sigma, y+j-sigma]
    return out

@ti.kernel
def blend():
    for i, j in canvas:
        canvas[i, j] += bloom_img[i, j]


if __name__ == "__main__":
    init_gauss()
    camera = Camera()
    gui = ti.GUI("Black Hole", res=(image_width, image_height))
    canvas.fill(0)
    cnt = 0
    while gui.running:
        render()
        cnt += 1
        gui.set_image(np.sqrt(bloom_img.to_numpy() / cnt))
        gui.show()
