import taichi as ti
ti.init(arch=ti.gpu)

res = (900,900)
Pi = 3.14159265

R0 = 1.5
rs = 1.0
dphi = 0.01
n = 1000
line_num = 100

r0 = 2.0   #1.22474

main_pos = ti.Vector([5.0, 0.0, 0.0])
main_dir = ti.Vector([0.0, 0.0, 0.0])
vup = ti.Vector([0.0, 1.0, 0.0])

phi = ti.field(dtype=ti.f32, shape=n)
u = ti.field(dtype=ti.f32, shape=(line_num, n))
v = ti.field(dtype=ti.f32, shape=(line_num, n))
v0 = ti.field(dtype=ti.f32, shape=line_num)
pos = ti.Vector.field(2, dtype=ti.f32, shape=line_num*n)
pos_down = ti.Vector.field(2, dtype=ti.f32, shape=line_num*n)
bh_pos = ti.Vector.field(2, dtype=ti.f32, shape=1)

window = ti.ui.Window("Black Hole", res=res)
canvas = window.get_canvas()


@ti.kernel
def set_initial_v():
    for i in range(line_num):
        v0[i] = 1.0 * ti.tan((i/line_num - 0.5) * Pi)
        # v = ti.Vector([-4, 1]).normalized()
        # x = ti.Vector([1, 0])
        # v0[i] = -ti.cos(ti.acos(v.dot(x)))/(ti.sin(ti.acos(v.dot(x))) * r0)

@ti.kernel
def init(r0: ti.f32):
    bh_pos[0] = ti.Vector([0,0]) + (0.5, 0.5)
    y = main_pos.cross(main_dir).normalized()
    x = main_pos.normalized()
    z = x.cross(y)
    for i in range(line_num):
        u[i, 0] = 1/r0
        v[i, 0] = v0[i]
    for i in phi:
        phi[i] = i*dphi

@ti.func
def euler(l):
    for i in range(1, n):
        v[l, i] = v[l, i-1] - u[l, i-1] * (1 - 3/2 * u[l, i-1]**2) * dphi
        u[l, i] = u[l, i - 1] + v[l, i] * dphi

        if 1/u[l, i] > 100:
            u[l, i] = 100.0
            v[l, i] = 0.0
        elif 1/u[l, i] < 0.01:
            u[l, i] = 100.0
            v[l, i] = 0.0


@ti.kernel
def calculate_traj():
    for l in range(line_num):
        euler(l)

@ti.kernel
def polar2xyz():
    for l in range(line_num):
        for i in range(n):
            pos[l * n + i][0] = 1/u[l, i] * ti.cos(phi[i]) / 5.0 + 0.5
            pos[l * n + i][1] = 1/u[l, i] * ti.sin(phi[i]) / 5.0 + 0.5
            # pos_down[l * n + i][0] = 1/u[l, i] * ti.cos(phi[i]) / 5.0 + 0.5
            # pos_down[l * n + i][1] = - 1/u[l, i] * ti.sin(phi[i]) / 5.0 + 0.5


def main():
    set_initial_v()
    init(1/r0)
    calculate_traj()
    polar2xyz()
    canvas.set_background_color((0.2,0.2,0.5))
    while window.running:
    # for i in range(1):
        canvas.circles(bh_pos, rs/10.0, (0,0,0))
        canvas.circles(pos, 0.001, (1,1,1))
        window.show()
        init(r0)
        calculate_traj()
        polar2xyz()


if __name__ == "__main__":
    main()
