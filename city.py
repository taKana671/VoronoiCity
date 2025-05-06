import random
from enum import Enum

from panda3d.bullet import BulletRigidBodyNode
from panda3d.bullet import BulletTriangleMeshShape, BulletHeightfieldShape, ZUp
from panda3d.bullet import BulletConvexHullShape, BulletTriangleMesh, BulletConvexHullShape, BulletCylinderShape
from panda3d.core import NodePath, PandaNode
from panda3d.core import BitMask32, Vec3, Point3, LColor
from panda3d.core import TransformState

from shapes.src import Cylinder, EllipticalPrism, Capsule, CapsulePrism, RoundedCornerBox, Sphere, Torus, Cone


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

    def assemble(self, building, makers):
        for pos, hpr, maker in makers:
            model = maker.create()
            building.assemble(model, pos, hpr)

        self.attach(building)

    def stack_alternating_boxes(self, building, n, maker_1, maker_2, attach=True):
        z = 0

        for i in range(n):
            maker = maker_1 if i % 2 == 0 else maker_2
            z += 0 if i == 0 else maker.height / 2
            model = maker.create()
            building.assemble(model, Point3(0, 0, z), Vec3(0, 0, 0))
            z += maker.height / 2

        if attach:
            self.attach(building)

    def stack_alternating_prisms(self, building, n, maker_1, maker_2, attach=True):
        z = 0

        for i in range(n):
            maker = maker_1 if i % 2 == 0 else maker_2
            model = maker.create()
            building.assemble(model, Point3(0, 0, z), Vec3(0, 0, 0))
            z += maker.height

        if attach:
            self.attach(building)


class Area1(City):

    def build(self):
        # ##### area1-2 #####

        building = Building('area12_0', Point3(-105, 120, 0), Vec3(0, 0, 0))
        maker_1 = Cylinder(radius=7, height=6, segs_a=3)
        maker_2 = Cylinder(radius=5, height=0.5, segs_a=1)
        self.stack_alternating_prisms(building, 15, maker_1, maker_2)

        # ##### area1-4 #####
        building = Building('area14_0', Point3(-121, 85, 3), Vec3(90, 0, 0))
        args = dict(corner_radius=4, rounded_f_left=False, rounded_f_right=False)
        maker_1 = RoundedCornerBox(width=30, depth=10, height=6, corner_radius=4, segs_w=15, segs_d=5, segs_z=3)
        maker_2 = RoundedCornerBox(width=28, depth=8, height=0.5, corner_radius=4, segs_w=14, segs_d=4, segs_z=1)
        self.stack_alternating_prisms(building, 7, maker_1, maker_2)

        # ##### area1-5 #####
        building = Building('area55_0', Point3(-112, 42, 3), Vec3(66, 0, 0))

        maker_1 = RoundedCornerBox(width=40, depth=17, height=6, segs_w=20, segs_d=5, segs_z=10, corner_radius=4)
        maker_2 = RoundedCornerBox(width=38, depth=15, height=0.5, segs_w=20, segs_d=5, segs_z=1, corner_radius=4)
        self.stack_alternating_boxes(building, 5, maker_1, maker_2, attach=False)

        model = CapsulePrism(width=6, depth=12, height=17, segs_w=5, segs_d=5, segs_z=20, rounded_right=False).create()
        building.assemble(model, Point3(0, 0, 18), Vec3(90, 0, 90))
        self.attach(building)


        # ##### area1-3 #####

        building = Building('area1_cy1', Point3(-54, 108, 0), Vec3(0, 0, 0))
        args = [dict(radius=15, height=20, segs_a=10), dict(radius=10, height=5, segs_a=3)]
        self.stack_cylinder(building, args)

        rb = [
            # [Point3(-121, 76, 12.5), Vec3(36, 0, 0), dict(width=8, depth=8, height=25, segs_w=4, segs_d=4, segs_z=10, corner_radius=2)],
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
        building = Building('area2_cy0', Point3(20, 28, 0), Vec3(78, 0, 0))
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
        for i, (pos, args) in enumerate(cy):
            building = Building(f'area2_cy{i + 1}', pos, Vec3(0, 0, 0))
            building.build(Cylinder(**args).create())
            self.attach(building)

        # double layer cylinder
        building = Building('area1_cy3', Point3(-32, 19, 0), Vec3(0, 0, 0))
        args = [dict(radius=7, height=15, segs_a=5), dict(radius=6, height=3, segs_a=3)]
        self.stack_cylinder(building, args)

        # double layer rounded corner boxes, same center
        building = Building('area2_rb0', Point3(36, 20, 12.5), Vec3(-40, 0, 0))
        args = [
            dict(width=15, depth=15, height=25, segs_w=5, segs_d=5, segs_z=10, corner_radius=2),
            dict(width=10, depth=10, height=5, segs_w=4, segs_d=4, segs_z=2, corner_radius=2)
        ]
        self.stack_box(building, args)

        building = Building('area2_rb1', Point3(-25, 40, 2.5), Vec3(10, 0, 0))
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
        for i, (pos, hpr, args) in enumerate(cp):
            building = Building(f'area1_cp{input}', pos, hpr)
            model = CapsulePrism(**args).create()
            building.build(model)
            self.attach(building)


class Aera3(City):

    def build(self):
        # double layer rounded corner boxes, same center
        building = Building('area3_rb0', Point3(41, 120, 18), Vec3(0, 0, 0))
        args = [
            dict(width=35, depth=12, height=36, segs_w=10, segs_d=5, segs_z=15, corner_radius=3),
            dict(width=30, depth=7, height=4, segs_w=5, segs_d=5, segs_z=2, corner_radius=3)
        ]
        self.stack_box(building, args)

        building = Building('area3_rb1', Point3(112, 19, 7.5), Vec3(-30, 0, 0))
        args = [
            dict(width=20, depth=15, height=15, segs_w=10, segs_d=5, segs_z=5, corner_radius=2),
            dict(width=15, depth=10, height=3, segs_w=5, segs_d=5, segs_z=2, corner_radius=2)
        ]
        self.stack_box(building, args)

        # rounded corner boxe having cylinder on the top
        building = Building('area3_rb2', Point3(110, 103, 25), Vec3(0, 0, 0))
        model_1 = RoundedCornerBox(
            width=30, depth=30, height=50, segs_w=15, segs_d=15, segs_z=25, corner_radius=2).create()
        model_2 = Cylinder(radius=12, height=5, segs_a=2).create()

        for i, model in enumerate([model_1, model_2]):
            building.assemble(model, Point3(0, 0, i * 25), Vec3(0, 0, 0))

        self.attach(building)

        # triple layer cylinders
        building = Building('area3_cy0', Point3(85, 110, 0), Vec3(0, 0, 0))
        args = [
            dict(radius=8, height=15, segs_a=4),
            dict(radius=6, height=20, segs_a=10),
            dict(radius=4, height=10, segs_a=5)
        ]
        self.stack_cylinder(building, args)

        # one quarter capsule
        building = Building('area3_cp0', Point3(96, 44, 1), Vec3(46, 0, 0))
        li = [
            [Point3(0, 0, 0), Vec3(0, 0, 0), CapsulePrism(width=30, depth=30, height=2, segs_w=15, segs_d=15, segs_z=2)],
            [Point3(0, 0, 2), Vec3(0, 0, 0), CapsulePrism(width=25, depth=25, height=2, segs_w=5, segs_d=5, segs_z=2)],
            [Point3(11, 2, 3), Vec3(0, 0, -90), Capsule(radius=12, inner_radius=10, height=22, segs_a=6, ring_slice_deg=270)]
        ]

        for pos, hpr, maker in li:
            model = maker.create()
            building.assemble(model, pos, hpr)

        self.attach(building)


class Area4(City):

    def build(self):
        # double layer rounded corner boxes, same center
        building = Building('area4_rb1', Point3(-119, -66, 7.5), Vec3(92, 0, 0))
        args = [
            dict(width=50, depth=10, height=15, segs_w=15, segs_d=5, segs_z=5, corner_radius=2),
            dict(width=48, depth=8, height=3, segs_w=14, segs_d=6, segs_z=2, corner_radius=2)
        ]
        self.stack_box(building, args)

        # sphere dome
        building = Building('area4_sp0', Point3(-78, -101, 1), Vec3(0, 0, 0))
        li = [
            [Point3(0, 0, 0), Cylinder(radius=22, height=2, segs_bottom_cap=11, segs_top_cap=11)],
            [Point3(0, 0, 2), Cylinder(radius=20, height=2, segs_bottom_cap=10, segs_top_cap=10)],
            [Point3(0, 0, 4), Cylinder(radius=18, height=2, segs_bottom_cap=9, segs_top_cap=9)],
            [Point3(0, 0, 6), Sphere(radius=16, inner_radius=14, slice_deg=120, bottom_clip=0, top_clip=0.8, segs_bottom_cap=8, segs_top_cap=4)]
        ]

        for pos, maker in li:
            model = maker.create()
            building.assemble(model, pos, Vec3(0, 0, 0))

        self.attach(building)

        # two rounded corner boxes
        li = [
            [Point3(-55, -121, 15), Vec3(-86, 0, 0), 30],
            [Point3(-48, -112, 7.5), Vec3(-86, 0, 0), 15]
        ]

        for i, (pos, hpr, h) in enumerate(li):
            building = Building(f'area4_rb2_{i}', pos, hpr)
            model = RoundedCornerBox(
                width=10, depth=10, height=h, corner_radius=5, rounded_b_left=False, rounded_f_right=False
            ).create()
            building.build(model)
            self.attach(building)


class Area6(City):

    def build(self):
        # one corner rounded box, 3 stacked
        building = Building('area6_rb0', Point3(-72, 22, 5), Vec3(-68, 0, 0))
        start_w, diff = 40, 10

        for i in range(3):
            h = 20 if i == 0 else 5
            x = -(diff / 2) * i
            z = 0 if i == 0 else 12.5 + h * (i - 1)
            w = start_w - diff * i

            model = RoundedCornerBox(
                width=w, depth=20, height=h, corner_radius=10,
                rounded_b_left=False, rounded_b_right=False, rounded_f_left=False
            ).create()
            building.assemble(model, Point3(x, 0, z), Vec3(0, 0, 0))

        self.attach(building)

        # two layer of capsule prism and rounded corner box
        hc, hr = 5, 15
        building = Building('area6_cp0', Point3(-104, 1, hc / 2), Vec3(64, 0, 0))
        li = [
            CapsulePrism(width=30, depth=15, height=hc, segs_w=10, segs_d=5, segs_z=int(hc / 2)),
            RoundedCornerBox(width=30, depth=10, height=hr, corner_radius=2, segs_w=15, segs_d=5, segs_z=int(hr / 2))
        ]

        for i, maker in enumerate(li):
            h = 0 if i == 0 else (hc + hr) / 2
            model = maker.create()
            building.assemble(model, Point3(0, 0, h), Vec3(0, 0, 0))

        self.attach(building)

        # three cylinders with different height
        h, r = 50, 3
        building = Building('area6_cy0', Point3(-87, -7, 0), Vec3(-24, 0, 0))

        for i, (x, y) in enumerate([(-r, 0), (0, r * 3 ** 0.5), (r, 0)]):
            height = h - i * 10
            maker = Cylinder(radius=r, height=height, segs_a=int(height / 2))
            model = maker.create()
            building.assemble(model, Point3(x, y, 0), Vec3(0, 0, 0))

        self.attach(building)

        # two corner rounded box, 3 stacked
        building = Building('area6_rb1', Point3(-91, -48, 5), Vec3(-76, 0, 0))
        start_w, diff = 40, 5

        for i in range(3):
            w = start_w - diff * i
            d = 20 - diff * i
            h = 20 if i == 0 else 5
            z = 0 if i == 0 else 12.5 + h * (i - 1)
            x = -(diff / 2) * i
            y = -(diff / 2) * i

            model = RoundedCornerBox(
                width=w, depth=d, height=h, corner_radius=5, rounded_b_right=False, rounded_f_left=False
            ).create()
            building.assemble(model, Point3(x, y, z), Vec3(0, 0, 0))

        self.attach(building)

        # sphere dome
        building = Building('area6_sp0', Point3(-70, -20, 0), Vec3(22, 0, 0))
        model = Sphere(radius=15, inner_radius=13, slice_deg=170, bottom_clip=0).create()
        building.build(model)
        self.attach(building)

        # 4 elliptical prism, different height
        building = Building('area6_cy0', Point3(-67, -48, 0), Vec3(38, 0, 0))

        for i, (x, y) in enumerate([(0, 6), (-4, 0), (4, 0), (0, -6)]):
            h = 45 - i * 8
            model = EllipticalPrism(major_axis=4, minor_axis=3, height=h, segs_a=5).create()
            building.assemble(model, Point3(x, y, 0), Vec3(0, 0, 0))

        self.attach(building)

        # sphere dome
        building = Building('area4_sp1', Point3(-9, -99, 1), Vec3(-138, 0, 0))

        li = [
            Cylinder(radius=22, height=2, segs_bottom_cap=11, segs_top_cap=11, ring_slice_deg=180),
            Cylinder(radius=20, height=2, segs_bottom_cap=10, segs_top_cap=10, ring_slice_deg=180),
            Cylinder(radius=18, height=2, segs_bottom_cap=9, segs_top_cap=9, ring_slice_deg=180),
            Sphere(radius=16, inner_radius=14, slice_deg=180, bottom_clip=0, segs_bottom_cap=8, segs_top_cap=8)
        ]

        for i, maker in enumerate(li):
            model = maker.create()
            building.assemble(model, Point3(0, -2 * i, 2 * i), Vec3(0, 0, 0))

        self.attach(building)

        # rounded corner box with cylinder on the top
        building = Building('area4_rb2', Point3(-33, -63, 1), Vec3(-34, 0, 0))
        li = [
            [Point3(0, 0, 10), Vec3(0, 0, 0), RoundedCornerBox(width=30, depth=20, height=18, segs_w=4, segs_d=4, segs_z=5, corner_radius=5)],
            [Point3(-7, 0, 18), Vec3(0, 0, 0), Cylinder(radius=7, height=6, segs_a=3, segs_bottom_cap=3, segs_top_cap=3)]
        ]
        for pos, hpr, maker in li:
            model = maker.create()
            building.assemble(model, pos, hpr)

        self.attach(building)

        # three layer cylinders
        building = Building('area2_cy0', Point3(-42, -80, 0), Vec3(0, 0, 0))
        args = [
            dict(radius=8, height=10, segs_a=5),
            dict(radius=6, height=20, segs_a=15),
            dict(radius=4, height=20, segs_a=15)
        ]
        self.stack_cylinder(building, args)


class Area7(City):

    def build(self):
        # triple layer capsule prism, different w, d, h
        building = Building('area7_cp0', Point3(3, -19, 7.5), Vec3(-20, 0, 0))
        start_w, start_d = 30, 25
        diff = 5
        z = 0

        for i in range(3):
            h = 15 if i == 0 else 4
            w = start_w - diff * i
            d = start_d - diff * i
            z += (0 if i == 0 else h / 2)
            pos = Point3(diff / 2 * i, -diff / 2 * i, z)

            model = CapsulePrism(
                width=w, depth=d, height=h, segs_w=int(w / 2), segs_d=int(d / 2),
                segs_z=int(h / 2), rounded_right=False
            ).create()

            building.assemble(model, pos, Vec3(0, 0, 0))
            z += h / 2

        self.attach(building)

        # multi layer sylinder, different center y
        building = Building('area7_cy0', Point3(-35, -19, 0), Vec3(4, 0, 0))
        n, v, h = 10, 4, 6

        for i in range(n):
            model = Cylinder(radius=6, height=h, segs_a=3).create()
            y = 0 if i == 0 or i == n - 1 else (v if i % 2 == 0 else -v)
            building.assemble(model, Point3(0, y, h * i), Vec3(0, 0, 0))

        self.attach(building)

        # double layer two rounded corner boxes, different h, w, d
        building = Building('area7_rb0', Point3(-12, -43, 5), Vec3(-34, 0, 0))
        diff = 5
        z = 0

        for i in range(2):
            w = 35 - diff * i
            d = 20 - diff * i
            h = 10 if i == 0 else 5
            z += (0 if i == 0 else h / 2)
            pos = Point3(-diff / 2 * i, diff / 2 * i, z)

            model = RoundedCornerBox(
                width=w, depth=d, height=h, corner_radius=d / 2, segs_w=int(w / 2), segs_d=int(d / 2),
                segs_z=int(h / 2), rounded_b_left=False, rounded_f_right=False
            ).create()

            building.assemble(model, pos, Vec3(0, 0, 0))
            z += h / 2

        self.attach(building)

        # half torus
        building = Building('area4_tr0', Point3(18, -58, 3.5), Vec3(-104, 0, 0))
        model = Torus(ring_radius=9, section_radius=4, ring_slice_deg=180, section_slice_deg=90).create()
        building.build(model)
        self.attach(building)

        # hollow cylinder
        building = Building('area4_cy1', Point3(33, -49, 0), Vec3(82, 0, 0))
        hz = 0

        li = [
            dict(radius=22, height=2, segs_bottom_cap=11, segs_top_cap=11),
            dict(radius=20, height=2, segs_bottom_cap=10, segs_top_cap=10),
            dict(radius=18, height=2, segs_bottom_cap=9, segs_top_cap=9),
            dict(radius=16, inner_radius=14, height=15)
        ]

        for i, d in enumerate(li):
            args = dict(**d, ring_slice_deg=180)
            model = Cylinder(**args).create()
            z = hz if i == len(li) - 1 else 2 * i

            building.assemble(model, Point3(0, -2 * i, z), Vec3(0, 0, 0))
            hz += args['height']

        self.attach(building)

        # multi layer corner rounded boxes, different angle
        building = Building('area7_rb1', Point3(55, -6, 2.5), Vec3(-28, 0, 0))
        z, h = 0, 5

        for i in range(9):
            model = RoundedCornerBox(width=20, depth=20, height=5, corner_radius=5).create()
            angle = 0 if i % 2 == 0 else 45
            building.assemble(model, Point3(0, 0, z), Vec3(angle, 0, 0))
            z += h

        self.attach(building)

        building = Building('area7_cp1', Point3(77, -12, 5), Vec3(76, 0, 0))

        args = [
            dict(width=16, depth=14, height=10, segs_w=8, segs_d=7, segs_z=5),
            dict(width=14, depth=12, height=2, segs_w=7, segs_d=6, segs_z=2),
        ]
        self.stack_capsule_prizm(building, args)

        building = Building('area7_cp2', Point3(93, -17, 5), Vec3(76, 0, 0))

        args = [
            dict(width=16, depth=14, height=10, segs_w=8, segs_d=7, segs_z=5),
            dict(width=14, depth=12, height=2, segs_w=7, segs_d=6, segs_z=2),
        ]
        self.stack_capsule_prizm(building, args)

        # two layer of capsule prism and rounded corner box
        hc, hr = 5, 10
        building = Building('area7_cp3', Point3(73, -60, hc / 2), Vec3(16, 0, 0))
        li = [
            CapsulePrism(width=20, depth=15, height=hc, segs_w=10, segs_d=5, segs_z=int(hc / 2)),
            RoundedCornerBox(width=25, depth=10, height=hr, corner_radius=2, segs_w=15, segs_d=5, segs_z=int(hr / 2))
        ]

        for i, maker in enumerate(li):
            h = 0 if i == 0 else (hc + hr) / 2
            model = maker.create()
            building.assemble(model, Point3(0, 0, h), Vec3(0, 0, 0))

        self.attach(building)

        # multi layer corner rounded boxes, different angle
        building = Building('area7_rb2', Point3(68, -44, 2.5), Vec3(0, 0, 0))
        z, h = 0, 5

        for i in range(12):
            model = RoundedCornerBox(width=10, depth=10, height=5, corner_radius=2).create()
            angle = 0 if i % 2 == 0 else 45
            building.assemble(model, Point3(0, 0, z), Vec3(angle, 0, 0))
            z += h

        self.attach(building)


class Aera5(City):

    def build(self):
        # ##### area5-1 #####

        building = Building('area51_0', Point3(4.2, -111, 3.5), Vec3(44, 0, 0))
        model = Torus(ring_radius=9, section_radius=4, ring_slice_deg=180, section_slice_deg=90).create()
        building.build(model)
        self.attach(building)

        # ##### area5-2 #####

        # parking
        building = Building('area52_0', Point3(44, -88, 0), Vec3(0, 0, 0))
        args = dict(slice_deg=180, bottom_clip=0, top_clip=0.5)
        li = [
            [Point3(0, 0, 0), Vec3(0, 0, 0), Sphere(radius=20, inner_radius=19, **args)],
            [Point3(0, 0, 10), Vec3(0, 0, 0), Sphere(radius=16, inner_radius=15, **args)]
        ]
        self.assemble(building, li)

        building = Building('area52_1', Point3(57, -116, 2.5), Vec3(0, 0, 0))
        args = dict(corner_radius=5, rounded_b_right=False)
        maker_1 = RoundedCornerBox(width=20, depth=15, height=5, **args)
        maker_2 = RoundedCornerBox(width=18, depth=13, height=0.5, **args)
        self.stack_alternating_boxes(building, 13, maker_1, maker_2)

        # ##### area5-3 #####

        building = Building('area53_0', Point3(103, -113, 2.5), Vec3(-18, 0, 0))
        args = dict(width=25, depth=20, height=5, segs_w=5, segs_d=4, segs_z=2, corner_radius=10)
        maker_1 = RoundedCornerBox(**args, rounded_f_left=False, rounded_b_right=False)
        maker_2 = RoundedCornerBox(**args, rounded_f_right=False, rounded_b_left=False)
        self.stack_alternating_boxes(building, 10, maker_1, maker_2)

        # hollow cylinder pair
        building = Building('area53_1', Point3(91, -88, 0), Vec3(14, 0, 0))
        args = dict(radius=8, inner_radius=6, ring_slice_deg=180)
        li = [
            [Point3(0, 0, 0), Vec3(0, 0, 0), Cylinder(**args, height=15, segs_a=5)],
            [Point3(-5, 0, 0), Vec3(180, 0, 0), Cylinder(**args, height=10, segs_a=5)],
        ]
        self.assemble(building, li)

        # ##### area5-4 #####

        building = Building('area54_0', Point3(119, -77, 0), Vec3(196, 0, 0))
        maker_1 = Cylinder(radius=8, height=5, segs_a=2, segs_bottom_cap=4, segs_top_cap=4)
        maker_2 = Cylinder(radius=6, height=0.5, segs_a=2)
        self.stack_alternating_prisms(building, 16, maker_1, maker_2)

        # ##### area5-5 #####

        building = Building('area55_0', Point3(119, -39, 2.5), Vec3(90, 0, 0))

        maker_1 = RoundedCornerBox(width=40, depth=15, height=5, segs_w=20, segs_d=5, segs_z=10, corner_radius=4)
        maker_2 = RoundedCornerBox(width=38, depth=12, height=0.5, segs_w=20, segs_d=5, segs_z=1, corner_radius=4)
        self.stack_alternating_boxes(building, 9, maker_1, maker_2, attach=False)

        model = CapsulePrism(width=6, depth=12, height=15, segs_w=5, segs_d=5, segs_z=20, rounded_right=False).create()
        building.assemble(model, Point3(0, 0, 25), Vec3(90, 0, 90))
        self.attach(building)


class AreaTree(City):

    def __init__(self):
        self.model = base.loader.load_model('models/pinetree/tree2.bam')

    def build(self):
        tree_pos = [
            # Area1
            (-92, 125, 0),
            (-126, 121, 0),
            (-124, 125, 0),
            (-118, 15, 0),
            (-120, 7.6, 0),
            (-125, -3.1, 0),
            (-125, 16, 0),


            (31, 6, 0),
            (-44, 66, 0),
            (14, 77, 0),
            (-0.2, 36, 0),
            (42, 31, 0),
            (46, 54, 0),
            (55, 49, 0),


            # Area3
            (20, 114, 0),
            (17, 121, 0),
            (114, 33, 0),
            (124, 34, 0),
            (122, 43, 0),
            (93, 13, 0),

            # Area4
            (-17, -126, 0),
            (-24, -126, 0),
            (-120, -125, 0),
            (-113, -125, 0),
            (-116, -96, 0),
            (-126, -101, 0),
            (-118, -36, 0),
            (-122, -32, 0),
            (-104, -101, 0),
            (-109, -109, 0),
            (-104, -115, 0),
            (-44, -123, 0),

            # Area6
            (-78, 49, 0),
            (-86, 45, 0),
            (-75, -6, 0),
            (-96, -13, 0),
            (-94, 30, 0),
            (-56, -41, 0),
            (-53, -32, 0),
            (-72, -61, 0),
            (-2, -75, 0),
            (-11, -69, 0),
            (-58, -71, 0),
            (-54, -61, 0),
            (-37, -100, 0),
            (-43, -94, 0),

            # Area7
            (-25, -2.5, 0),
            (-37, -2.9, 0),
            (20, -39, 0),
            (21, -29, 0),
            (69, 8, 0),
            (61, 13, 0),
            (82, -42, 0),
            (49, -71, 0),

            # Area5
            (23, -114, 0),
            (28, -121, 0),
            (15, -123, 0),
            (106, -50, 0),
            (106, -58, 0),
            (115, -14, 0),
            (122, -8, 0),
            (123, -91, 0),
            (125, -98, 0),
            (104, -97, 0),
            (79, -104, 0),
            (82, -116, 0),
            (37, -112, 0),
            (41, -121, 0)

        ]

        for i, pos in enumerate(tree_pos):
            tree = PineTree(self.model, i)
            tree.set_pos(pos)
            self.attach(tree)
