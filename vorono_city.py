import sys

import cv2
import numpy as np

from panda3d.bullet import BulletWorld, BulletDebugNode
from direct.showbase.ShowBase import ShowBase
from direct.showbase.ShowBaseGlobal import globalClock
from panda3d.core import Point3, Vec3, Vec2
from panda3d.core import NodePath
from panda3d.core import TransparencyAttrib, AntialiasAttrib

from panda3d.core import load_prc_file_data

from shapes.src.box import Box
from shapes.src import IrregularPrism
from scene import Scene


load_prc_file_data("", """
    textures-power-2 none
    gl-coordinate-system default
    window-title Panda3D Voronoi City
    filled-wireframe-apply-shader true
    stm-max-views 8
    stm-max-chunk-count 2048
    framebuffer-multisample 1
    multisamples 2""")


class Marbles(ShowBase):

    def __init__(self):
        super().__init__()

        self.disable_mouse()
        self.render.set_antialias(AntialiasAttrib.MAuto)

        self.world = BulletWorld()
        self.world.set_gravity(Vec3(0, 0, -9.81))

        self.debug = self.render.attach_new_node(BulletDebugNode('debug'))
        self.world.set_debug_node(self.debug.node())

        self.scene = Scene()

        self.camera_root = NodePath('camera_root')
        self.camera_root.reparent_to(self.render)

        self.camera.set_pos(Point3(0, -300, 200))
        self.camera.look_at(Point3(0, 0, 0))
        self.camera.reparent_to(self.camera_root)

        self.dragging = False
        self.before_mouse_pos = None

        # self.model = Box(2, 2, 2).create()
        # self.model.reparent_to(self.render)
        # pts = [
        #     [130, 215],
        #     [140, 255],
        #     [189, 255],
        #     [191, 225],
        #     [153, 206],
        # ]

        # pts = [
        #     [64, 255],
        #     [57, 244],
        #     [14, 255],
        # ]
        # pts = [
        #     [255, 64],
        #     [244, 57],
        #     [255, 14],
        # ]

        # tmp = [Vec2(*pt) for pt in pts]
        # center = self.calculate_center(tmp)
        # self.model = IrregularPrism([pt - center for pt in tmp], height=10).create()
        # self.model.reparent_to(self.render)
        # tex = self.loader.load_texture('brick.jpg')
        # self.model.set_texture(tex)
        # self.create_3d_regions()

        self.accept('escape', sys.exit)
        self.accept('mouse1', self.mouse_click)
        self.accept('mouse1-up', self.mouse_release)
        self.accept('d', self.toggle_debug)
        self.taskMgr.add(self.update, 'update')

    def change_coords(self, vert):
        size = 256
        half_size = size / 2

        x = vert[0] - half_size

        if vert[1] <= half_size:
            y = half_size - vert[1]
        else:
            y = size - vert[1] - half_size

        return x, y

    # def create_3d_regions(self):
    #     size = 256
    #     half_size = size / 2

    #     for vertices in self.generate_vertices():
    #         # v = [Vec2(*vert[::-1]) for vert in vertices]
    #         v = [Vec2(*self.change_coords(vert)) for vert in vertices]
    #         print('coords changed', v)
    #         center = self.calculate_centroid(v)
    #         # pos = self.calculate_center(v)
    #         # center = self.calculate_center(v)
    #         print('center', center)
    #         v = [vert - center for vert in v]
    #         # import pdb; pdb.set_trace()
    #         print('moved vertices', v)
    #         model = IrregularPrism(v, height=10).create()
    #         tex = self.loader.load_texture('brick.jpg')
    #         model.set_texture(tex)

    #         # x = center.x - half_size

    #         # if center.y <= half_size:
    #         #     y = half_size - center.y
    #         # else:
    #         #     y = center.y - half_size

    #         pos = Point3(center.xy, 0)
    #         # pos = Point3(0,0,0)
    #         model.set_pos_hpr(pos, Vec3(0, 0, 0))
    #         model.reparent_to(self.render)

    # def generate_vertices(self):
    #     img = cv2.imread('dst.png')
    #     # kernel = np.ones((3, 3), np.uint8)
    #     # img = cv2.erode(img, kernel, iterations=2)
    #     # img = cv2.resize(dst,(64, 64))
    #     # import pdb; pdb.set_trace()

    #     img_gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)

    #     ret, region = cv2.threshold(img_gray, 1, 255, cv2.THRESH_BINARY)
    #     contours, _ = cv2.findContours(region, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    #     # import pdb; pdb.set_trace()
    #     for i, cont in enumerate(contours):
    #         arclen = cv2.arcLength(cont, True)
    #         approx = cv2.approxPolyDP(cont, 0.01 * arclen, True)
    #         # vertices = [vert.ravel() for vert in approx]
    #         vertices = [np.array([64, 255], dtype=np.int32), np.array([14, 255], dtype=np.int32), np.array([57, 244], dtype=np.int32)]
    #         print(vertices)
    #         yield vertices

    #         if i == 0:
    #             break
   

            # for pt in approx:
            #     x, y = pt.ravel()
            #     yield x, y

    # def calculate_centroid(self, pts):
    #     n = len(pts)
    #     area = 0.
    #     x = y = 0
    #     areas = 0

    #     for i in range(2, n):
    #         pt1 = pts[0]
    #         pt2 = pts[i - 1]
    #         pt3 = pts[i]

    #         area = (pt2.x - pt1.x) * (pt3.y - pt1.y) - (pt2.y - pt1.y) * (pt3.x - pt1.x)
    #         pt = (pt1 + pt2 + pt3) / 3
    #         x += area * pt.x
    #         y += area * pt.y
    #         areas += area
        
    #     return Vec2(x / areas, y / areas)

    # def calculate_centroid(self, pts):
    #     n = len(pts)
    #     area = 0.

    #     centroid_x = 0.
    #     centroid_y = 0.

    #     for i in range(n):
    #         x_i, y_i = pts[i]
    #         x_next, y_next = pts[(i + 1) % n]
    #         cross_prod = (x_i * y_next) - (x_next * y_i)
    #         area += cross_prod

    #         centroid_x += (x_i + x_next) * cross_prod
    #         centroid_y += (y_i + y_next) * cross_prod

    #     area = area / 2.0
    #     centroid_x = centroid_x / (n * area)
    #     centroid_y = centroid_y / (n * area)

    #     return Vec2(centroid_x, centroid_y)


    # def calculate_center(self, pts):
    #     total = Vec2()

    #     for pt in pts:
    #         total += pt

    #     return total / len(pts)

    def toggle_debug(self):
        # self.toggle_wireframe()
        if self.debug.is_hidden():
            self.debug.show()
        else:
            self.debug.hide()

    def mouse_click(self):
        self.dragging = True
        self.dragging_start_time = globalClock.get_frame_time()

    def mouse_release(self):
        self.dragging = False
        self.before_mouse_pos = None

    def rotate_camera(self, mouse_pos, dt):
        if self.before_mouse_pos:
            angle = Vec3()

            if (delta := mouse_pos.x - self.before_mouse_pos.x) < 0:
                angle.x += 180
            elif delta > 0:
                angle.x -= 180

            if (delta := mouse_pos.y - self.before_mouse_pos.y) < 0:
                angle.z -= 180
            elif delta > 0:
                angle.z += 180

            angle *= dt
            self.camera_root.set_hpr(self.camera_root.get_hpr() + angle)

        self.before_mouse_pos = Vec2(mouse_pos.xy)

    def update(self, task):
        dt = globalClock.get_dt()

        if self.mouseWatcherNode.has_mouse():
            mouse_pos = self.mouseWatcherNode.get_mouse()

            if self.dragging:
                if globalClock.get_frame_time() - self.dragging_start_time >= 0.2:
                    self.rotate_camera(mouse_pos, dt)

        self.world.do_physics(dt)
        return task.cont


if __name__ == '__main__':
    app = Marbles()
    app.run()