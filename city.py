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

    def stack_cylinder(self, building, args_li):
        z = 0

        for args in args_li:
            model = Cylinder(**args).create()
            building.assemble(model, Point3(0, 0, z), Vec3(0, 0, 0))
            z += args['height']

        self.attach(building)

    def stack_elliptical_prism(self, building, args_li):
        z = 0

        for args in args_li:
            model = EllipticalPrism(**args).create()
            building.assemble(model, Point3(0, 0, z), Vec3(0, 0, 0))
            z += args['height']

        self.attach(building)

    def stack_box(self, building, args_li):
        z = 0

        for i, args in enumerate(args_li):
            if i > 0:
                before_args = args_li[i - 1]
                z += (before_args['height'] + args['height']) / 2

            model = RoundedCornerBox(**args).create()
            building.assemble(model, Point3(0, 0, z), Vec3(0, 0, 0))

        self.attach(building)

    def stack_capsule_prizm(self, building, args_li):
        z = 0

        for i, args in enumerate(args_li):
            if i > 0:
                before_args = args_li[i - 1]
                z += (before_args['height'] + args['height']) / 2

            model = CapsulePrism(**args).create()
            building.assemble(model, Point3(0, 0, z), Vec3(0, 0, 0))

        self.attach(building)


class Area1(City):

    def build(self):
        building = Building('area1_ep0', Point3(-108, 120, 0), Vec3(-56, 0, 0))
        model = EllipticalPrism(major_axis=8, minor_axis=4, height=30, segs_a=15).create()
        building.build(model)
        self.attach(building)

        building = Building('area1_cy0', Point3(-98, 122, 0), Vec3(0, 0, 0))
        model = Cylinder(radius=3, height=20, segs_a=20).create()
        building.build(model)
        self.attach(building)

        building = Building('area1_cy1', Point3(-54, 108, 0), Vec3(0, 0, 0))
        args = [dict(radius=15, height=20, segs_a=10), dict(radius=10, height=5, segs_a=3)]
        self.stack_cylinder(building, args)

        cp = [
            [Point3(-117, 36, 7.5), Vec3(82, 0, 90), dict(width=15, depth=10, height=40, segs_w=5, segs_d=5, segs_z=20, rounded_right=False)],
            [Point3(-121, 93, 7.5), Vec3(-64, 0, 0), dict(width=10, depth=5, height=15, segs_w=5, segs_d=2, segs_z=15)]
        ]
        for i, (pos, hpr, args) in enumerate(cp):
            building = Building(f'area1_cp{i}', pos, hpr)
            model = CapsulePrism(**args).create()
            building.build(model)
            self.attach(building)

        rb = [
            [Point3(-121, 76, 12.5), Vec3(36, 0, 0), dict(width=8, depth=8, height=25, segs_w=4, segs_d=4, segs_z=10, corner_radius=2)],
            [Point3(-77, 85, 6), Vec3(-32, 0, 0), dict(width=40, depth=20, height=12, segs_w=20, segs_d=10, segs_z=6, corner_radius=2)],
            [Point3(-77, 116, 10), Vec3(-32, 0, 0), dict(width=10, depth=10, height=20, segs_w=5, segs_d=5, segs_z=10, corner_radius=1)]
        ]
        for i, (pos, hpr, args) in enumerate(rb):
            building = Building(f'area1_rb{i}', pos, hpr)
            model = RoundedCornerBox(**args).create()
            building.build(model)
            self.attach(building)


class Area2(City):

    def build(self):
        # sphere dome
        building = Building('area2_sp0', Point3(13, 6, 0), Vec3(164, 0, 0))
        model = Sphere(radius=14, inner_radius=12, slice_deg=170, bottom_clip=0).create()
        building.build(model)
        self.attach(building)

        # double layer and different height cylinder
        building = Building('area2_cy1', Point3(20, 28, 0), Vec3(78, 0, 0))
        cy = [
            [0, 0, dict(radius=8, height=10, segs_a=5)],
            [5, 0, dict(radius=6, height=30, segs_a=15, ring_slice_deg=180)],
            [5, 180, dict(radius=6, height=20, segs_a=15, ring_slice_deg=180)]
        ]
        for z, h, args in cy:
            model = Cylinder(**args).create()
            building.assemble(model, Point3(0, 0, z), Vec3(h, 0, 0))

        self.attach(building)

        # tall cylinder
        cy = [
            [Point3(-22, 97, 0), dict(radius=6, height=50, segs_a=10)],
            [Point3(5, 48, 0), dict(radius=5, height=30, segs_a=15)]
        ]
        for pos, args in cy:
            building = Building('area2_cy2', pos, Vec3(0, 0, 0))
            building.build(Cylinder(**args).create())
            self.attach(building)

        # double layer cylinder
        building = Building('area1_cy4', Point3(-32, 19, 0), Vec3(0, 0, 0))
        args = [dict(radius=7, height=15, segs_a=5), dict(radius=6, height=3, segs_a=3)]
        self.stack_cylinder(building, args)

        # double layer rounded corner boxes, same center
        building = Building('area2_rb1', Point3(36, 20, 12.5), Vec3(-40, 0, 0))
        args = [
            dict(width=15, depth=15, height=25, segs_w=5, segs_d=5, segs_z=10, corner_radius=2),
            dict(width=10, depth=10, height=5, segs_w=4, segs_d=4, segs_z=2, corner_radius=2)
        ]
        self.stack_box(building, args)

        building = Building('area2_rb3', Point3(-25, 40, 2.5), Vec3(10, 0, 0))
        args = [
            dict(width=40, depth=20, height=5, segs_w=20, segs_d=10, segs_z=3, corner_radius=4),
            dict(width=35, depth=15, height=20, segs_w=10, segs_d=5, segs_z=5, corner_radius=4),
        ]
        self.stack_box(building, args)

        # double layer rounded corner boxes with different width, offset center
        building = Building('area2_rb2', Point3(-18, 74, 6), Vec3(10, 0, 0))
        rb = [
            [0, 0, dict(width=40, depth=20, height=12, segs_w=20, segs_d=10, segs_z=6, corner_radius=2)],
            [11, 5, dict(width=20, depth=15, height=10, segs_w=15, segs_d=5, segs_z=3, corner_radius=2)],
        ]
        for z, x, args in rb:
            model = RoundedCornerBox(**args).create()
            building.assemble(model, Point3(x, 0, z), Vec3(0, 0, 0))

        self.attach(building)

        # double layer capsule prism
        building = Building('area2_cp0', Point3(2, 102, 15), Vec3(-52, 0, 0))
        args = [
            dict(width=20, depth=20, height=30, segs_w=10, segs_d=10, segs_z=15),
            dict(width=18, depth=18, height=2.5, segs_w=9, segs_d=9, segs_z=2),
        ]
        self.stack_capsule_prizm(building, args)

        building = Building('area2_cp1', Point3(71, 66, 7.5), Vec3(48, 0, 0))
        args = [
            dict(width=20, depth=15, height=15, segs_w=10, segs_d=5, segs_z=5),
            dict(width=18, depth=13, height=5, segs_w=9, segs_d=6, segs_z=3),
        ]
        self.stack_capsule_prizm(building, args)

        building = Building('area2_cp2', Point3(58, 77, 7.5), Vec3(48, 0, 0))
        args = [
            dict(width=25, depth=15, height=20, segs_w=5, segs_d=3, segs_z=10),
            dict(width=23, depth=13, height=5, segs_w=5, segs_d=4, segs_z=3),
        ]
        self.stack_capsule_prizm(building, args)

        # double layer elliptical prism, different rotation angle
        building = Building('area1_ep0', Point3(-14, 22, 0), Vec3(224, 0, 0))
        ep = [
            [0, dict(major_axis=10, minor_axis=5, height=35, segs_a=5)],
            [35, dict(major_axis=10, minor_axis=5, height=5, segs_a=3, ring_slice_deg=180)],
        ]
        for z, args in ep:
            model = EllipticalPrism(**args).create()
            building.assemble(model, Point3(0, 0, z), Vec3(0, 0, 0))
        self.attach(building)

        # double layer elliptical prism
        building = Building('area1_ep1', Point3(31, 41, 0), Vec3(146, 0, 0))
        args = [
            dict(major_axis=8, minor_axis=4, height=20, segs_a=10),
            dict(major_axis=6, minor_axis=2, height=4, segs_a=2),
        ]
        self.stack_elliptical_prism(building, args)

        # capsule prism
        cp = [
            [Point3(37, 81, 2.5), Vec3(140, 0, 90), dict(width=5, depth=10, height=15, segs_w=2, segs_d=5, segs_z=5, rounded_right=False)],
            [Point3(46, 92, 2.5), Vec3(140, 0, 90), dict(width=5, depth=10, height=10, segs_w=2, segs_d=5, segs_z=5, rounded_right=False)]
        ]
        for pos, hpr, args in cp:
            building = Building('area1_cp1', pos, hpr)
            model = CapsulePrism(**args).create()
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
            (-124, 9, 0),
            (-107, 61, 0),
            (-102, 51, 0),
            (31, 6, 0),
            (-44, 66, 0),
            (14, 77, 0),
            (-0.2, 36, 0),
            (42, 31, 0),
            (46, 54, 0),
            (55, 49, 0),
            (58, 95, 0)
        ]

        for i, pos in enumerate(tree_pos):
            tree = PineTree(self.model, i)
            tree.set_pos(pos)
            self.attach(tree)
