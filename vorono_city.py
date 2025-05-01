import sys

import cv2
import numpy as np

from panda3d.bullet import BulletWorld, BulletDebugNode
from direct.showbase.ShowBase import ShowBase
from direct.showbase.ShowBaseGlobal import globalClock
from panda3d.core import Point3, Vec3, Vec2, BitMask32
from panda3d.core import NodePath
from panda3d.core import TransparencyAttrib, AntialiasAttrib

from panda3d.core import load_prc_file_data

from shapes.src.box import Box
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
        self.scene.create_city()

        self.camera_root = NodePath('camera_root')
        self.camera_root.reparent_to(self.render)

        self.camera.set_pos(Point3(0, -300, 200))
        self.camera.look_at(Point3(0, 0, 0))
        self.camera.reparent_to(self.camera_root)

        self.clicked = False
        self.dragging = False
        self.before_mouse_pos = None
        self.target = None

        self.accept('escape', sys.exit)
        self.accept('mouse1', self.mouse_click)
        self.accept('mouse1-up', self.mouse_release)
        self.accept('d', self.toggle_debug)
        self.accept('i', self.get_target_info)
        self.accept('r', self.release_target)

        self.accept('x', self.positioning, ['x', 1])
        self.accept('shift-x', self.positioning, ['x', -1])
        self.accept('y', self.positioning, ['y', 1])
        self.accept('shift-y', self.positioning, ['y', -1])
        self.accept('z', self.positioning, ['z', 1])
        self.accept('shift-z', self.positioning, ['z', -1])
        self.accept('h', self.positioning, ['h', 1])
        self.accept('shift-h', self.positioning, ['h', -1])

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

    def click(self, mouse_pos):
        print('clicked!')
        near_pos = Point3()
        far_pos = Point3()
        self.camLens.extrude(mouse_pos, near_pos, far_pos)

        from_pos = self.render.get_relative_point(self.cam, near_pos)
        to_pos = self.render.get_relative_point(self.cam, far_pos)

        if (result := self.world.ray_test_closest(
                from_pos, to_pos, BitMask32.bit(1))).has_hit():

            match result.get_node().get_tag('category'):
                case 'ground':
                    print(result.get_hit_pos())

                case 'object':
                    print('set target')
                    self.target = NodePath(result.get_node())

            # print(result.get_node())
            # print(result.get_node().get_name())
            # print(result.get_node().get_tag('category'))
            # print(result.get_hit_pos())

    def release_target(self):
        if self.target is not None:
            self.target = None

    def get_target_info(self):
        if self.target is not None:
            print(f'pos: {self.target.get_pos()}, hpr: {self.target.get_hpr()}')

    def positioning(self, key, direction):
        if self.target is not None:
            distance = 1
            angle = 2
            pos = Point3()
            hpr = Vec3()

            match key:
                case 'x':
                    pos.x = distance * direction

                case 'y':
                    pos.y = distance * direction

                case 'z':
                    pos.z = distance * direction

                case 'h':
                    hpr.x = angle * direction

            pos = self.target.get_pos() + pos
            hpr = self.target.get_hpr() + hpr
            self.target.set_pos_hpr(pos, hpr)

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
        if globalClock.get_frame_time() - self.dragging_start_time < 0.2:
            self.clicked = True

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

            if self.clicked:
                self.click(mouse_pos)
                self.clicked = False

            if self.dragging:
                if globalClock.get_frame_time() - self.dragging_start_time >= 0.2:
                    self.rotate_camera(mouse_pos, dt)

        self.world.do_physics(dt)
        return task.cont


if __name__ == '__main__':
    app = Marbles()
    app.run()