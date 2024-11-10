from taichi_glsl import *

PI = 3.14159265


@ti.data_oriented
class Ray:
    def __init__(self, origin, direction):
        self.origin = origin
        self.direction = direction

    @ti.func
    def update_euler(self):
        color = ti.Vector([0.0, 0.0, 0.0])
        origin = self.origin
        direction = self.direction.normalized()
        x = origin.normalized()
        y = direction.cross(x).normalized()
        z = x.cross(y)
        A_no = ti.Matrix.cols([x, y, z])  # coordinate transformation new -> old
        A_on = A_no.inverse()             # coordinate transformation old -> new
        phi = 0.0
        dphi = 0.001

        dudphi = -ti.cos(ti.acos(x.dot(direction))) / (ti.sin(ti.acos(x.dot(direction))) * origin.norm())
        accre_l = (A_on @ y.cross(ti.Vector([0, 1, 0]))).normalized()
        accre_phi1 = atan(accre_l[2] / accre_l[0]) % (2 * PI)
        accre_phi2 = (atan(accre_l[2] / accre_l[0]) + PI) % (2 * PI)
        u = 1 / origin.norm()

        for i in range(10000):
            phi += dphi
            phi %= 2 * PI
            dudphi += - u * (1 - 3 / 2 * u) * dphi
            u += dudphi * dphi
            r = 1/u
            if r > 500:
                break
            if r < 0.01:
                break
            if (phi - accre_phi1) * (phi - dphi - accre_phi1) <= 0 or (phi - accre_phi2) * (phi - dphi - accre_phi2) <= 0:
                # add the mapping to the accretion disk
                if 2.5 < r < 5:
                    color += ti.Vector([1/(exp((r-4.9)/0.03)+1), 2/(exp((r-5)/0.3)+1)-1, -(r+3)**3*(r-5)/432])
        return color


@ti.data_oriented
class Camera:
    def __init__(self, fov=60, aspect_ratio=16/9):
        # Camera parameters
        self.lookfrom = ti.Vector.field(3, dtype=ti.f32, shape=())
        self.lookat = ti.Vector.field(3, dtype=ti.f32, shape=())
        self.vup = ti.Vector.field(3, dtype=ti.f32, shape=())
        self.fov = fov
        self.aspect_ratio = aspect_ratio

        self.cam_lower_left_corner = ti.Vector.field(3, dtype=ti.f32, shape=())
        self.cam_horizontal = ti.Vector.field(3, dtype=ti.f32, shape=())
        self.cam_vertical = ti.Vector.field(3, dtype=ti.f32, shape=())
        self.cam_origin = ti.Vector.field(3, dtype=ti.f32, shape=())
        self.reset()

    @ti.kernel
    def reset(self):
        self.lookfrom[None] = [5.0, 1.0, 0.0]
        self.lookat[None] = [2.0, 0.0, -3.0]
        self.vup[None] = [0.0, 1.0, 0.0]
        theta = self.fov * (PI / 180.0)
        half_height = ti.tan(theta / 2.0)
        half_width = self.aspect_ratio * half_height
        self.cam_origin[None] = self.lookfrom[None]
        w = (self.lookfrom[None] - self.lookat[None]).normalized()
        u = (self.vup[None].cross(w)).normalized()
        v = w.cross(u)
        self.cam_lower_left_corner[None] = ti.Vector([-half_width, -half_height, -1.0])
        self.cam_lower_left_corner[
            None] = self.cam_origin[None] - half_width * u - half_height * v - w
        self.cam_horizontal[None] = 2 * half_width * u
        self.cam_vertical[None] = 2 * half_height * v

    @ti.kernel
    def reset_after_move(self):
        self.cam_origin[None] = self.lookfrom[None]
        w = (self.lookfrom[None] - self.lookat[None]).normalized()
        u = (self.vup[None].cross(w)).normalized()
        v = w.cross(u)
        theta = self.fov * (PI / 180.0)
        half_height = ti.tan(theta / 2.0)
        half_width = self.aspect_ratio * half_height
        self.cam_lower_left_corner[None] = ti.Vector([-half_width, -half_height, -1.0])
        self.cam_lower_left_corner[
            None] = self.cam_origin[None] - half_width * u - half_height * v - w
        self.cam_horizontal[None] = 2 * half_width * u
        self.cam_vertical[None] = 2 * half_height * v

    def rot_z(self, t):
        self.lookfrom[None][0] = 9.0 * cos(t/100)
        self.lookfrom[None][1] = 9.0 * sin(t/100)
        self.reset_after_move()

    @ti.func
    def get_ray(self, u, v):
        return Ray(self.cam_origin[None],
                   self.cam_lower_left_corner[None] + u * self.cam_horizontal[None] + v * self.cam_vertical[None] -
                   self.cam_origin[None])
