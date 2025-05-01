import random
from enum import Enum

from panda3d.bullet import BulletRigidBodyNode
from panda3d.bullet import BulletTriangleMeshShape, BulletHeightfieldShape, ZUp
from panda3d.bullet import BulletConvexHullShape, BulletTriangleMesh, BulletConvexHullShape, BulletCylinderShape
from panda3d.core import NodePath, PandaNode
from panda3d.core import BitMask32, Vec3, Point3, LColor
from panda3d.core import TransformState

from shapes.src import Cylinder, EllipticalPrism, Capsule, CapsulePrism, RoundedCornerBox, Sphere


class Color(Enum):

    # COLOR_01 = (0.9, 0.2, 1.0)
    # COLOR_02 = (0.38, 0.59, 1.0)
    # COLOR_03 = (0.37, 0.0, 1.0)
    # COLOR_04 = (0.76, 0.19, 1.0)
    # COLOR_05 = (0.67, 0.92, 1.0)
    # COLOR_06 = (0.58, 0.38, 1.0)
    # COLOR_07 = (0.98, 0.62, 1.0)
    # COLOR_08 = (0.94, 0.99, 1.0)
    # COLOR_09 = (0.69, 0.93, 1.0)
    # COLOR_10 = (0.71, 0.14, 1.0)
    # COLOR_11 = (0.23, 0.24, 1.0)
    # COLOR_12 = (0.07, 0.85, 1.0)
    # COLOR_13 = (0.64, 0.21, 1.0)
    # COLOR_14 = (0.53, 0.72, 1.0)
    # COLOR_15 = (0.99, 0.71, 1.0)
    # COLOR_16 = (0.83, 0.95, 1.0)
    # COLOR_17 = (0.78, 0.65, 1.0)
    # COLOR_18 = (0.65, 0.81, 1.0)
    # COLOR_19 = (0.49, 0.93, 1.0)
    # COLOR_20 = (0.92, 0.8, 1.0)
    # COLOR_21 = (0.94, 0.9, 1.0)
    # COLOR_22 = (0.16, 0.14, 1.0)
    # COLOR_23 = (0.28, 0.42, 1.0)
    # COLOR_24 = (0.12, 0.72, 1.0)
    # COLOR_25 = (0.07, 0.44, 1.0)
    # COLOR_26 = (0.67, 0.91, 1.0)


    COLOR_01 = (1.0, 0.9, 0.2)
    COLOR_02 = (1.0, 0.38, 0.59)
    COLOR_03 = (1.0, 0.37, 0.0)
    COLOR_04 = (1.0, 0.76, 0.19)
    COLOR_05 = (1.0, 0.67, 0.92)
    COLOR_06 = (1.0, 0.58, 0.38)
    COLOR_07 = (1.0, 0.98, 0.62)
    COLOR_08 = (1.0, 0.94, 0.99)
    COLOR_09 = (1.0, 0.69, 0.93)
    COLOR_10 = (1.0, 0.71, 0.14)
    COLOR_11 = (1.0, 0.23, 0.24)
    COLOR_12 = (1.0, 0.07, 0.85)
    COLOR_13 = (1.0, 0.64, 0.21)
    COLOR_14 = (1.0, 0.53, 0.72)
    COLOR_15 = (1.0, 0.99, 0.71)
    COLOR_16 = (1.0, 0.83, 0.95)
    COLOR_17 = (1.0, 0.78, 0.65)
    COLOR_18 = (1.0, 0.65, 0.81)
    COLOR_19 = (1.0, 0.49, 0.93)
    COLOR_20 = (1.0, 0.92, 0.8)
    COLOR_21 = (1.0, 0.94, 0.9)
    COLOR_22 = (1.0, 0.16, 0.14)
    COLOR_23 = (1.0, 0.28, 0.42)
    COLOR_24 = (1.0, 0.12, 0.72)
    COLOR_25 = (1.0, 0.07, 0.44)
    COLOR_26 = (1.0, 0.67, 0.91)

    @classmethod
    def random_choice(cls):
        c = random.choice(list(cls))
        return LColor(*c.value, 1)


class Building(NodePath):

    def __init__(self, name, pos, hpr):
        super().__init__(BulletRigidBodyNode(f'building_{name}'))
        self.set_tag('category', 'object')
        self.node().set_mass(0)
        self.set_collide_mask(BitMask32.bit(1))
        self.set_pos_hpr(pos, hpr)
        self.set_color(Color.random_choice())

    def make_convex_shape(self, model):
        shape = BulletConvexHullShape()
        shape.add_geom(model.node().get_geom(0))
        return shape

    def build(self, model):
        shape = self.make_convex_shape(model)
        self.node().add_shape(shape)
        model.reparent_to(self)

    def assemble(self, model, pos, hpr):
        shape = self.make_convex_shape(model)
        self.node().add_shape(shape, TransformState.make_pos_hpr(pos, hpr))
        model.set_pos_hpr(pos, hpr)
        model.reparent_to(self)


class CapsuleDome(NodePath):

    def __init__(self, name, radius, height, inner_radius=0, slice_deg=0,
                 top_hemisphere=True, bottom_hemisphere=True):
        super().__init__(BulletRigidBodyNode(f'capsule_dome_{name}'))
        self.set_tag('category', 'object')

        self.model = Capsule(
            radius=radius,
            inner_radius=inner_radius,
            height=height,
            segs_a=int(height),
            ring_slice_deg=slice_deg,
            top_hemisphere=top_hemisphere,
            bottom_hemisphere=bottom_hemisphere
        ).create()

        self.model.reparent_to(self)
        self.set_color(Color.random_choice())

        shape = BulletConvexHullShape()
        shape.add_geom(self.model.node().get_geom(0))
        self.node().add_shape(shape)
        self.node().set_mass(0)
        self.set_collide_mask(BitMask32.bit(1))


class SphereDome(NodePath):

    def __init__(self, name, radius, inner_radius=0, slice_deg=0, bottom_clip=0, top_clip=1):
        super().__init__(BulletRigidBodyNode(f'sphere_dome_{name}'))
        self.set_tag('category', 'object')

        self.model = Sphere(
            radius=radius,
            inner_radius=inner_radius,
            slice_deg=slice_deg,
            bottom_clip=bottom_clip,
            top_clip=top_clip
        ).create()

        self.model.reparent_to(self)
        self.set_color(Color.random_choice())

        shape = BulletConvexHullShape()
        shape.add_geom(self.model.node().get_geom(0))
        self.node().add_shape(shape)
        self.node().set_mass(0)
        self.set_collide_mask(BitMask32.bit(1))


class PineTree(NodePath):

    def __init__(self, model, name, scale=1.5):
        super().__init__(BulletRigidBodyNode(f'tree_{name}'))
        tree = model.copy_to(self)
        tree.set_transform(TransformState.make_pos(Vec3(-0.25, -0.15, 0)))
        tree.reparent_to(self)

        end, tip = tree.get_tight_bounds()
        height = (tip - end).z
        shape = BulletCylinderShape(0.3, height, ZUp)
        self.node().add_shape(shape)
        self.set_collide_mask(BitMask32.bit(1))
        self.set_scale(scale)


class City:

    areas = []

    def __init_subclass__(cls):
        super().__init_subclass__()
        if 'build' not in cls.__dict__:
            raise NotImplementedError('Subclasses must implement build method')

        City.areas.append(cls)

    def attach(self, model):
        model.reparent_to(base.scene.city_root)
        base.world.attach(model.node())


class Area1(City):

    def build(self):
        building = Building('area1_0', Point3(-108, 120, 0), Vec3(-56, 0, 0))
        model = EllipticalPrism(major_axis=8, minor_axis=4, height=30, segs_a=15).create()
        building.build(model)
        self.attach(building)

        building = Building('area1_1', Point3(-98, 122, 0), Vec3(0, 0, 0))
        model = Cylinder(radius=3, height=20, segs_a=20).create()
        building.build(model)
        self.attach(building)

        building = Building('area1_2', Point3(-54, 108, 0), Vec3(0, 0, 0))
        for r, h, z in [[15, 20, 0], [10, 5, 20]]:
            model = Cylinder(radius=r, height=h, segs_a=h).create()
            building.assemble(model, Point3(0, 0, z), Vec3(0, 0, 0))

        self.attach(building)

        building = Building('area1_3', Point3(-121, 93, 7.5), Vec3(-64, 0, 0))
        model = CapsulePrism(
            width=10, depth=5, height=15, segs_w=5, segs_d=2, segs_z=15).create()
        building.build(model)
        self.attach(building)

        rect = [
            [Point3(-121, 76, 12.5), Vec3(36, 0, 0), 8, 8, 25, 2],
            [Point3(-77, 85, 6), Vec3(-32, 0, 0), 40, 20, 12, 2],
            [Point3(-77, 116, 10), Vec3(-32, 0, 0), 10, 10, 20, 1]
        ]
        for pos, hpr, w, d, h, cr in rect:
            building = Building('area1', pos, hpr)
            model = RoundedCornerBox(
                width=w, depth=d, height=h, corner_radius=cr, segs_w=w, segs_d=d, segs_z=h).create()
            building.build(model)
            self.attach(building)


class AreaTree(City):

    def __init__(self):
        self.model = base.loader.load_model('models/pinetree/tree2.bam')

    def build(self):
        tree_pos = [
            (-126, 121, 0),
            (-124, 125, 0),
            (-113, 82, 0),
        ]

        for i, pos in enumerate(tree_pos):
            tree = PineTree(self.model, i)
            tree.set_pos(pos)
            self.attach(tree)
















