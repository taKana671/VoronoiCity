import math

from panda3d.bullet import BulletRigidBodyNode
from panda3d.bullet import BulletTriangleMeshShape, BulletHeightfieldShape, ZUp
from panda3d.bullet import BulletConvexHullShape, BulletTriangleMesh, BulletConvexHullShape
from panda3d.core import NodePath, PandaNode
from panda3d.core import BitMask32, Vec3, Point3, LColor
from panda3d.core import Filename, PNMImage
from panda3d.core import GeoMipTerrain
from panda3d.core import Shader, TextureStage, TransformState
from panda3d.core import TransparencyAttrib


from shapes.src import Plane, Cylinder, Box
from lights import BasicAmbientLight, BasicDayLight


class Ground(NodePath):

    def __init__(self, w=256, d=256, segs_w=16, segs_d=16):
        super().__init__(BulletRigidBodyNode('ground'))

        plane = Plane(w, d, segs_w, segs_d)
        self.model = plane.create()
        self.model.set_texture(base.loader.load_texture('voronoi_region2.png'))
        self.model.set_pos(0, 0, 0)
        self.model.reparent_to(self)

        mesh = BulletTriangleMesh()
        mesh.add_geom(self.model.node().get_geom(0))
        shape = BulletTriangleMeshShape(mesh, dynamic=False)
        self.node().add_shape(shape)

        self.node().set_mass(0)
        self.set_collide_mask(BitMask32.bit(1))


class RoundedConerBox(NodePath):

    def __init__(self, corner_radius=5, width=20, depth=20, height=80):
        super().__init__(BulletRigidBodyNode('rounded_corner'))
        self.maker = Box(width, depth, height)
        self.corner_radius = corner_radius
        self.create_rounded_corner_box()

    def extend_sides(self, main_geom_nd):
        # Box maker of the right and left sides.
        rl = Box(self.corner_radius, self.maker.depth, self.maker.height)
        # Box maker of the back and front sides.
        bf = Box(self.maker.width, self.corner_radius, self.maker.height)

        axis_vec = Vec3(0, 0, 1)
        x = (self.maker.width + self.corner_radius) / 2.0
        y = (self.maker.depth + self.corner_radius) / 2.0

        li = [
            [rl, Vec3(-x, 0, 0)],
            [rl, Vec3(x, 0, 0)],
            [bf, Vec3(0, -y, 0)],
            [bf, Vec3(0, y, 0)]
        ]

        for maker, diff in li:
            new_geom_nd = maker.get_geom_node()
            center = self.maker.center + diff
            self.maker.merge_geom(main_geom_nd, new_geom_nd, axis_vec, center, 0)

    def create_corners(self, main_geom_nd):
        cylinder_maker = Cylinder(
            radius=self.corner_radius,
            height=self.maker.height,
            ring_slice_deg=270
        )

        axis_vec = Vec3(0, 0, 1)
        rotate_angle = 90
        x = self.maker.width / 2
        y = self.maker.depth / 2
        z = self.maker.height / 2

        centers = [
            Point3(x, -y, -z),
            Point3(x, y, -z),
            Point3(-x, y, -z),
            Point3(-x, -y, -z),
        ]

        for i, center in enumerate(centers):
            new_geom_nd = cylinder_maker.get_geom_node()
            angle = rotate_angle * i
            self.maker.merge_geom(main_geom_nd, new_geom_nd, axis_vec, center, angle)

    def create_rounded_corner_box(self):
        main_geom_nd = self.maker.get_geom_node()
        self.extend_sides(main_geom_nd)
        self.create_corners(main_geom_nd)

        self.model = self.maker.modeling(main_geom_nd)
        self.set_color(LColor(0, 0, 1, 1))
        self.model.reparent_to(self)

        shape = BulletConvexHullShape()
        shape.add_geom(self.model.node().get_geom(0))
        self.node().add_shape(shape)
        self.node().set_mass(0)
        self.set_collide_mask(BitMask32.bit(1))


class Tower(NodePath):

    def __init__(self):
        super().__init__(BulletRigidBodyNode('tower'))
        self.model = Cylinder(radius=10, height=20).create()

        # self.model = Box(20, 20, 20, 50, thickness=5, open_left=True).create()
        # self.model = RoundedConerBox(20, 20, 20, 50, thickness=5, open_left=True).create()
        self.set_pos(0, 0, 0)
        # self.set_color(LColor(0.98, 0.98, 0.82, 1))
        self.set_color(LColor(1, 0, 0, 1))
        self.model.reparent_to(self)

        shape = BulletConvexHullShape()
        shape.add_geom(self.model.node().get_geom(0))
        self.node().add_shape(shape)
        self.node().set_mass(0)
        self.set_collide_mask(BitMask32.bit(1))


class Scene(NodePath):

    def __init__(self):
        super().__init__(PandaNode('scene'))
        self.reparent_to(base.render)

        self.ambient_light = BasicAmbientLight()
        self.day_light = BasicDayLight()

        self.ground = Ground()
        self.ground.reparent_to(self)
        self.ground.set_pos(Point3(0, 0, 0))
        base.world.attach(self.ground.node())

        # self.tower = Tower()
        self.tower = RoundedConerBox()
        self.tower.reparent_to(self)
        self.tower.set_pos(Point3(0, 0, 0))
        base.world.attach(self.tower.node())
        self.tower.set_pos(0, 0, 25)




