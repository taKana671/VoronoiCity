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
from shapes.src import EllipticalPrism, RoundedCornerBox
from lights import BasicAmbientLight, BasicDayLight
from city import City


class Ground(NodePath):

    def __init__(self, w=256, d=256, segs_w=16, segs_d=16):
        super().__init__(BulletRigidBodyNode('ground'))

        plane = Plane(w, d, segs_w, segs_d)
        self.model = plane.create()
        self.model.set_texture(base.loader.load_texture('voronoi_region2.png'))
        self.model.set_pos(0, 0, 0)
        self.model.reparent_to(self)
        self.set_tag('category', 'ground')

        mesh = BulletTriangleMesh()
        mesh.add_geom(self.model.node().get_geom(0))
        shape = BulletTriangleMeshShape(mesh, dynamic=False)
        self.node().add_shape(shape)

        self.node().set_mass(0)
        self.set_collide_mask(BitMask32.bit(1))


class Tower(NodePath):

    def __init__(self):
        super().__init__(BulletRigidBodyNode('tower'))
        self.set_tag('category', 'object')
        # self.model = Cylinder(radius=10, height=20).create()

        # self.model = EllipticalPrism(major_axis=5, minor_axis=2, height=20).create()
        self.model = RoundedCornerBox(width=10, depth=10, height=20, corner_radius=2).create()

        # self.model = Box(20, 20, 20, 50, thickness=5, open_left=True).create()
        # self.model = RoundedConerBox(20, 20, 20, 50, thickness=5, open_left=True).create()
        self.set_pos(0, 0, 0)
        self.set_h(30)

        # self.set_color(LColor(0.98, 0.98, 0.82, 1))
        self.set_color(LColor(0.38, 0.59, 1.0, 1))
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

        self.city_root = NodePath('city')
        self.city_root.reparent_to(self)

        # self.tower = Tower()
        # # self.tower = RoundedConerBox()
        # self.tower.reparent_to(self.city_root)
        # self.tower.set_pos(Point3(0, 0, 0))
        # base.world.attach(self.tower.node())
        # self.tower.set_pos(0, 0, 10)

    def create_city(self):
        for area in City.areas:
            a = area()
            a.build()





