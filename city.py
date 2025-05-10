import random
from enum import Enum

from panda3d.bullet import BulletRigidBodyNode
from panda3d.bullet import BulletTriangleMeshShape, BulletHeightfieldShape, ZUp
from panda3d.bullet import BulletConvexHullShape, BulletTriangleMesh, BulletConvexHullShape, BulletCylinderShape
from panda3d.core import NodePath, PandaNode
from panda3d.core import BitMask32, Vec3, Point3, LColor
from panda3d.core import TransformState

from shapes.src import Cylinder, EllipticalPrism, Capsule, CapsulePrism, RoundedCornerBox, Sphere, Torus, Cone, RightTriangularPrism


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

    def assemble(self, building, makers, attach=True):
        for pos, hpr, maker in makers:
            model = maker.create()
            building.assemble(model, pos, hpr)

        if attach:
            self.attach(building)

    def stack_shifting_boxes(self, building, n, maker, dirs, shift, start_z=0):
        """dirs: [(0, -1), (1, 0), (0, 1), (-1, 0)]
        """
        z = 0

        for i in range(n):
            if i == 0:
                z += start_z
                # import pdb; pdb.set_trace()
                model = maker.create()
                building.assemble(model, Point3(0, 0, z), Vec3(0, 0, 0))
                continue

            for _x, _y in dirs:
                x = _x * shift
                y = _y * shift
                z += maker.height / 2

                model = maker.create()
                building.assemble(model, Point3(x, y, z), Vec3(0, 0, 0))
                z += maker.height / 2

        self.attach(building)

    def stack_alternating_box_center(self, building, n, maker_1, maker_2, dir_x=0, dir_y=0,
                                     shift_x=0, shift_y=0, start_x=0, start_y=0, start_z=0, ):
        z = 0

        for i in range(n):
            if i % 2 == 0:
                maker = maker_1
                x = start_x
                y = start_y
            else:
                maker = maker_2
                x = shift_x * dir_x + start_x
                y = shift_y * dir_y + start_y

            z += start_z if i == 0 else maker.height / 2

            model = maker.create()
            building.assemble(model, Point3(x, y, z), Vec3(0, 0, 0))
            z += maker.height / 2

        self.attach(building)

    def stack_alternating_boxes(self, building, n, maker_1, maker_2, x=0, y=0, start_z=0, h=0, attach=True):
        z = 0

        for i in range(n):
            maker = maker_1 if i % 2 == 0 else maker_2
            z += start_z if i == 0 else maker.height / 2
            model = maker.create()
            building.assemble(model, Point3(x, y, z), Vec3(h, 0, 0))
            z += maker.height / 2

        if attach:
            self.attach(building)

    def stack_shifting_prisms(self, building, n, maker, dirs, shift, start_z=0):
        """dirs: [(0, -1), (1, 0), (0, 1), (-1, 0)]
        """
        z = 0

        for i in range(n):
            if i == 0 or i == n - 1:
                z += start_z if i == 0 else maker.height
                model = maker.create()
                building.assemble(model, Point3(0, 0, z), Vec3(0, 0, 0))
                continue

            for _x, _y in dirs:
                x = _x * shift
                y = _y * shift
                z += maker.height

                model = maker.create()
                building.assemble(model, Point3(x, y, z), Vec3(0, 0, 0))

        self.attach(building)

    def stack_alternating_prisms(self, building, n, maker_1, maker_2, x=0, y=0, z=0, h=0, attach=True):

        for i in range(n):
            maker = maker_1 if i % 2 == 0 else maker_2
            model = maker.create()
            building.assemble(model, Point3(x, y, z), Vec3(h, 0, 0))
            z += maker.height

        if attach:
            self.attach(building)

    def stack_rotating_prisms(self, building, maker, n, angles, x=0, y=0, z=0, attach=True):
        z = 0

        for _ in range(n):
            for angle in angles:
                model = maker.create()
                building.assemble(model, Point3(x, y, z), Vec3(angle, 0, 0))
                z += maker.height

        if attach:
            self.attach(building)

    def stack_rotating_boxes(self, building, maker, n, angles, x=0, y=0, start_z=0, attach=True):
        z = 0
        i = 0

        for _ in range(n):
            for angle in angles:
                model = maker.create()
                z += start_z if i == 0 else maker.height / 2
                building.assemble(model, Point3(x, y, z), Vec3(angle, 0, 0))
                z += maker.height / 2
                i += 1

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
        self.stack_alternating_prisms(building, 11, maker_1, maker_2)

        # ##### area1-5 #####

        building = Building('area15_0', Point3(-112, 42, 3), Vec3(66, 0, 0))

        maker_1 = RoundedCornerBox(width=40, depth=17, height=6, segs_w=20, segs_d=5, segs_z=10, corner_radius=4)
        maker_2 = RoundedCornerBox(width=38, depth=15, height=0.5, segs_w=20, segs_d=5, segs_z=1, corner_radius=4)
        self.stack_alternating_boxes(building, 9, maker_1, maker_2, attach=False)

        model = CapsulePrism(width=6, depth=12, height=17, segs_w=5, segs_d=5, segs_z=20, rounded_right=False).create()
        building.assemble(model, Point3(0, 0, 30), Vec3(90, 0, 90))
        self.attach(building)

        # ##### area1-3 #####

        building = Building('area13_0', Point3(-78, 81, 2.5), Vec3(-28, 0, 0))
        args = dict(width=40, height=5, segs_w=20, segs_z=2, corner_radius=5)
        maker_1 = RoundedCornerBox(depth=20, segs_d=10, **args)
        maker_2 = RoundedCornerBox(depth=15, segs_d=5, **args)
        shift_y = (maker_1.depth - maker_2.depth) * 0.5
        self.stack_alternating_box_center(building, 4, maker_1, maker_2, dir_y=1, shift_y=shift_y)

        building = Building('area13_1', Point3(-54, 108, 3), Vec3(64, 0, 0))
        args = dict(width=10, height=6, segs_w=5, segs_z=3)
        maker_1 = CapsulePrism(depth=30, segs_d=10, **args)
        maker_2 = CapsulePrism(depth=25, segs_d=5, **args)
        shift_y = (maker_1.depth - maker_2.depth) * 0.5
        self.stack_alternating_box_center(building, 8, maker_1, maker_2, dir_y=1, shift_y=shift_y)

        building = Building('area13_2', Point3(-82, 120, 1.5), Vec3(42, 0, 0))
        model = Torus(ring_radius=8, section_radius=3, ring_slice_deg=180, section_slice_deg=90).create()
        building.build(model)
        self.attach(building)


class Area2(City):

    def build(self):
        # ##### area2-1 #####

        # building = Building('area21_0', Point3(-6, 115, 0), Vec3(0, 0, 0))
        # maker = EllipticalPrism(major_axis=8, minor_axis=4, height=5, segs_top_cap=2, segs_bottom_cap=2)
        # dirs = [(-1, 0), (1, 0)]
        # self.stack_shifting_prisms(building, 8, maker, dirs, 6)

        building = Building('area21_0', Point3(-6, 115, 0), Vec3(90, 0, 0))
        maker = RoundedCornerBox(width=15, depth=15, height=5, corner_radius=4, segs_w=4, segs_d=4)
        dirs = [(0, -1), (0, 1)]
        self.stack_shifting_prisms(building, 8, maker, dirs, 5, start_z=0)

        building = Building('area21_1', Point3(-3, 84, 2.5), Vec3(14, 0, 0))
        args_1 = dict(height=5, segs_z=2, rounded_right=False)
        args_2 = dict(height=0.5, segs_z=1, rounded_right=False)

        maker_1 = CapsulePrism(width=40, depth=30, segs_w=20, segs_d=15, **args_1)
        maker_2 = CapsulePrism(width=38, depth=28, segs_w=19, segs_d=14, **args_2)
        self.stack_alternating_boxes(building, 3, maker_1, maker_2, attach=False)

        maker_1 = CapsulePrism(width=18, depth=28, segs_w=9, segs_d=14, **args_2)
        maker_2 = CapsulePrism(width=20, depth=30, segs_w=10, segs_d=15, **args_1)
        # self.stack_alternating_boxes(building, 2, maker_1, maker_2, start_z=8, x=10)
        self.stack_alternating_boxes(building, 2, maker_1, maker_2, x=10, start_z=8)

        # ##### area2-2 #####

        building = Building('area22_0', Point3(57, 69, 2.5), Vec3(-42, 0, 0))
        args = dict(corner_radius=10, rounded_f_left=False)

        maker_1 = RoundedCornerBox(width=40, depth=42, height=5, segs_w=20, segs_d=21, **args)
        maker_2 = RoundedCornerBox(width=38, depth=40, height=0.5, segs_w=18, segs_d=20, **args)
        self.stack_alternating_boxes(building, 3, maker_1, maker_2, attach=False)

        maker_1 = RoundedCornerBox(width=30, depth=32, height=5, segs_w=15, segs_d=10, **args)
        maker_2 = RoundedCornerBox(width=28, depth=30, height=0.5, segs_w=14, segs_d=15, **args)
        self.stack_alternating_boxes(building, 3, maker_1, maker_2, start_z=11, x=-5, y=5)

        # ##### area2-3 #####

        building = Building('area23_0', Point3(-27, 33, 2.5), Vec3(-80, 0, 0))
        args = dict(corner_radius=8, rounded_b_right=False, rounded_f_left=False)

        maker_1 = RoundedCornerBox(width=34, depth=28, height=5, segs_w=17, segs_d=14, **args)
        maker_2 = RoundedCornerBox(width=32, depth=26, height=0.5, segs_w=16, segs_d=13, segs_z=1, **args)
        self.stack_alternating_boxes(building, 3, maker_1, maker_2, attach=False)

        maker_1 = RoundedCornerBox(width=28, depth=22, height=0.5, segs_w=14, segs_d=11, segs_z=1, **args)
        maker_2 = RoundedCornerBox(width=30, depth=24, height=5, segs_w=15, segs_d=12, **args)
        self.stack_alternating_boxes(building, 2, maker_1, maker_2, start_z=8, x=2, y=2, attach=False)

        maker_1 = RoundedCornerBox(width=24, depth=18, height=0.5, segs_w=12, segs_d=9, segs_z=1, **args)
        maker_2 = RoundedCornerBox(width=26, depth=20, height=5, segs_w=13, segs_d=10, **args)
        self.stack_alternating_boxes(building, 2, maker_1, maker_2, start_z=13.5, x=4, y=4)

        building = Building('area23_1', Point3(-1.8, 47, 2.5), Vec3(6, 0, 0))
        args = dict(corner_radius=5, rounded_b_right=False)
        maker_1 = RoundedCornerBox(width=20, depth=15, height=5, **args)
        maker_2 = RoundedCornerBox(width=18, depth=13, height=0.5, segs_z=1, **args)
        self.stack_alternating_boxes(building, 10, maker_1, maker_2)

        # ##### area2-4 #####

        building = Building('area24_0', Point3(25, 22, 2.5), Vec3(52, 0, 0))
        args = dict(corner_radius=8)

        maker_1 = RoundedCornerBox(width=44, depth=30, height=5, segs_w=20, segs_d=21, **args)
        maker_2 = RoundedCornerBox(width=43, depth=22, height=0.5, segs_w=18, segs_d=20, **args)
        self.stack_alternating_boxes(building, 3, maker_1, maker_2, attach=False)

        maker_1 = RoundedCornerBox(width=36, depth=22, height=5, segs_w=15, segs_d=10, **args)
        maker_2 = RoundedCornerBox(width=34, depth=20, height=0.5, segs_w=14, segs_d=15, **args)
        self.stack_alternating_boxes(building, 3, maker_1, maker_2, start_z=10.5)


class Aera3(City):

    def build(self):
        # ##### area3-1 #####

        building = Building('area31_0', Point3(41, 116, 0), Vec3(0, 0, 0))
        maker_1 = EllipticalPrism(major_axis=20, minor_axis=11, height=5, segs_a=5)
        maker_2 = EllipticalPrism(major_axis=18, minor_axis=9, height=0.5, segs_a=5)
        self.stack_alternating_prisms(building, 15, maker_1, maker_2)

        # ##### area3-2 #####

        building = Building('area32_0', Point3(104, 103, 2.5), Vec3(0, 0, 0))
        args = dict(height=5, segs_z=2, corner_radius=5)
        maker_1 = RoundedCornerBox(**args, width=30, depth=30, segs_w=15, segs_d=10)
        maker_2 = RoundedCornerBox(**args, width=20, depth=20, segs_w=10, segs_d=10)
        self.stack_alternating_boxes(building, 13, maker_1, maker_2)

        # ##### area3-3 #####

        building = Building('area33_0', Point3(96, 44, 1), Vec3(46, 0, 0))
        li = [
            [Point3(0, 0, 0), Vec3(0, 0, 0), CapsulePrism(width=30, depth=30, height=2, segs_w=15, segs_d=15, segs_z=2)],
            [Point3(0, 0, 2), Vec3(0, 0, 0), CapsulePrism(width=25, depth=25, height=2, segs_w=5, segs_d=5, segs_z=2)],
        ]

        for pos, hpr, maker in li:
            model = maker.create()
            building.assemble(model, pos, hpr)

        maker_1 = CapsulePrism(width=20, depth=20, height=5, segs_w=5, segs_d=5, segs_z=2)
        maker_2 = CapsulePrism(width=18, depth=18, height=0.5, segs_w=5, segs_d=5, segs_z=2)
        self.stack_alternating_boxes(building, 17, maker_1, maker_2)

        building = Building('area33_1', Point3(113, 16, 1.5), Vec3(0, 0, 0))
        model = Torus(ring_radius=9, section_radius=4, section_slice_deg=90).create()
        building.build(model)
        self.attach(building)


class Area4(City):

    def build(self):
        # ##### area4-1 #####

        building = Building('area41_0', Point3(-120, -66, 2.5), Vec3(90, 0, 0))
        args = dict(rounded_f_left=False, rounded_f_right=False)
        model = RoundedCornerBox(width=50, depth=15, height=5, corner_radius=5, **args).create()
        building.assemble(model, Point3(0, 0, 0), Vec3(0, 0, 0))

        args = dict(**args, corner_radius=3)
        maker_1 = RoundedCornerBox(width=50, depth=10, height=5, segs_w=25, segs_d=5, **args)
        maker_2 = RoundedCornerBox(width=48, depth=8, height=0.5, segs_w=24, segs_d=4, segs_z=1, **args)
        self.stack_alternating_boxes(building, 12, maker_1, maker_2, start_z=5, y=2)

        # ##### area4-2 #####
        building = Building('area42_0', Point3(-78, -101, 0), Vec3(0, 0, 0))
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

        building = Building('area42_1', Point3(-50, -118, 1.5), Vec3(0, 0, 0))
        model = Torus(ring_radius=6, section_radius=3, section_slice_deg=90).create()
        building.build(model)
        self.attach(building)


class Area6(City):

    def build(self):
        # ##### area6-1 #####

        building = Building('area61_0', Point3(-101, -2, 2.5), Vec3(0, 0, 0))
        maker = RoundedCornerBox(width=20, depth=20, height=5, segs_w=5, segs_d=5, segs_z=5, corner_radius=2)
        dirs = [(0, -1), (-1, 0)]
        self.stack_shifting_boxes(building, 6, maker, dirs, 5)

        building = Building('area61_1', Point3(-75, 21, 1), Vec3(-72, 0, 0))
        args = dict(height=2, segs_z=2)

        li = [
            [Point3(0, 0, 0), Vec3(0, 0, 0), CapsulePrism(width=22, depth=34, segs_w=11, segs_d=17, **args)],
            [Point3(0, 0, 2), Vec3(0, 0, 0), CapsulePrism(width=21, depth=29.5, segs_w=7, segs_d=10, **args)],
            [Point3(0, 0, 4), Vec3(0, 0, 0), CapsulePrism(width=20, depth=25, segs_w=10, segs_d=5, **args)],
            [Point3(9, 2, 5), Vec3(0, 0, -90), Capsule(radius=12, inner_radius=10, height=18, segs_a=6, ring_slice_deg=270)]
        ]

        for pos, hpr, maker in li:
            model = maker.create()
            building.assemble(model, pos, hpr)

        self.attach(building)

        # ##### area6-2 #####

        building = Building('area62_0', Point3(-72, -40, 0), Vec3(82, 0, 0))
        maker_1 = Cylinder(radius=18, inner_radius=13, height=5, segs_a=3, ring_slice_deg=120)
        maker_2 = Cylinder(radius=17, inner_radius=14, height=0.5, segs_a=1, ring_slice_deg=120)
        self.stack_alternating_prisms(building, 5, maker_1, maker_2, attach=False)

        maker_1 = Cylinder(radius=15, inner_radius=10, height=5, segs_a=3, ring_slice_deg=90)
        maker_2 = Cylinder(radius=14, inner_radius=11, height=0.5, segs_a=3, ring_slice_deg=90)
        self.stack_alternating_prisms(building, 15, maker_1, maker_2, x=-5, y=18, h=180)

        # ##### area6-3 #####

        building = Building('area63_0', Point3(-25, -99, 2.5), Vec3(-54, 0, 0))
        maker = RoundedCornerBox(width=18, depth=18, height=5, corner_radius=4)
        self.stack_rotating_boxes(building, maker, 6, [0, 45])

        building = Building('area63_1', Point3(-24, -69, 2.5), Vec3(-34, 0, 0))
        args_1 = dict(height=5, segs_z=2, rounded_left=False)
        args_2 = dict(height=0.5, segs_z=1, rounded_left=False)

        maker_1 = CapsulePrism(width=55, depth=15, segs_w=11, segs_d=5, **args_1)
        maker_2 = CapsulePrism(width=52, depth=12, segs_w=26, segs_d=6, **args_2)
        self.stack_alternating_boxes(building, 5, maker_1, maker_2, attach=False)

        maker_1 = CapsulePrism(width=10, depth=15, segs_w=5, segs_d=5, **args_1)
        maker_2 = CapsulePrism(width=8, depth=12, segs_w=4, segs_d=6, **args_2)
        self.stack_alternating_boxes(building, 5, maker_1, maker_2, h=-90, x=-20, y=-12.5)


        # n, v, h = 10, 4, 6
        # for i in range(n):
        #     model = Cylinder(radius=6, height=h, segs_a=3).create()
        #     y = 0 if i == 0 or i == n - 1 else (v if i % 2 == 0 else -v)
        #     building.assemble(model, Point3(0, y, h * i), Vec3(0, 0, 0))

        # self.attach(building)


        # building = Building('area63_0', Point3(-87, -48, 2.5), Vec3(-76, 0, 0))
        # args = dict(corner_radius=10, rounded_b_left=False, rounded_b_right=False, rounded_f_left=False)
        # args_visi = dict(height=5, segs_z=2, **args)
        # args_hide = dict(height=0.5, segs_z=1, **args)

        # maker = RoundedCornerBox(width=40, depth=26, segs_w=20, segs_d=13, **args_visi)
        # self.assemble(building, [[Point3(0, 0, 0), Vec3(0, 0, 0), maker]], attach=False)

        # diff_w = 10
        # diff_d = 2
        # start_z = maker.height
        # n = 2

        # for i in range(1, n + 1):
        #     w2 = maker.width - i * diff_w
        #     d2 = maker.depth - i * diff_d
        #     w1 = w2 - 2
        #     d1 = d2 - 2
        #     x = -diff_w / 2 * i
        #     y = -diff_d / 2 * i
        #     z = start_z - maker.height / 2

        #     maker_1 = RoundedCornerBox(width=w1, depth=d1, segs_w=int(w1 / 2), segs_d=int(d1 / 2), **args_hide)
        #     maker_2 = RoundedCornerBox(width=w2, depth=d2, segs_w=int(w2 / 2), segs_d=int(d2 / 2), **args_visi)
        #     attach = False if i < n - 1 else True

        #     self.stack_alternating_boxes(building, 2, maker_1, maker_2, start_z=z, x=x, y=y, attach=attach)
        #     start_z += maker_1.height + maker_2.height

        
        # building = Building('area71_0', Point3(-23, -98, 0), Vec3(4, 0, 0))
        # maker = Cylinder(radius=6, height=6, segs_a=3)
        # dirs = [(0, -1), (0, 1)]
        # self.stack_shifting_prisms(building, 8, maker, dirs, 4, start_z=0)


        # building = Building('area63_0', Point3(-23, -98, 0), Vec3(138, 0, 0))
        # maker_1 = Cylinder(radius=15, height=5, segs_c=8)
        # maker_2 = Cylinder(radius=13, height=0.5, segs_c=8)
        # self.stack_alternating_boxes(building, 10, maker_1, maker_2)

        # building = Building('area61_1', Point3(-69, 17, 0), Vec3(138, 0, 0))

        # maker_1 = Cylinder(radius=14, height=5)
        # maker_2 = Cylinder(radius=12, height=0.5)


        # # maker_1 = EllipticalPrism(major_axis=18, minor_axis=12, height=5, segs_a=5)
        # # maker_2 = EllipticalPrism(major_axis=16, minor_axis=10, height=0.5, segs_a=5)
        # self.stack_alternating_prisms(building, 5, maker_1, maker_2)

        # # maker_i 

        # maker_1 = Cylinder(radius=16, height=5)
        # maker_2 = Cylinder(radius=14, height=0.5)

        # maker_1 = CapsulePrism(width=10, depth=20, height=5)
        # maker_2 = CapsulePrism(width=16, depth=8, height=0.5)

        # maker_1 = EllipticalPrism(major_axis=16, minor_axis=8, height=5, segs_a=5)
        # maker_2 = EllipticalPrism(major_axis=14, minor_axis=6, height=0.5, segs_a=5)
        # self.stack_alternating_prisms(building, 2, maker_1, maker_2, x=-4, y=4, z=16)


        # one corner rounded box, 3 stacked
        # building = Building('area6_rb0', Point3(-88, -49, 5), Vec3(-68, 0, 0))
        # start_w, diff = 40, 10

        # for i in range(3):
        #     h = 20 if i == 0 else 5
        #     x = -(diff / 2) * i
        #     z = 0 if i == 0 else 12.5 + h * (i - 1)
        #     w = start_w - diff * i

        #     model = RoundedCornerBox(
        #         width=w, depth=20, height=h, corner_radius=10,
        #         rounded_b_left=False, rounded_b_right=False, rounded_f_left=False
        #     ).create()
        #     building.assemble(model, Point3(x, 0, z), Vec3(0, 0, 0))

        # self.attach(building)






        # # two layer of capsule prism and rounded corner box
        # hc, hr = 5, 15
        # building = Building('area6_cp0', Point3(-104, 1, hc / 2), Vec3(64, 0, 0))
        # li = [
        #     CapsulePrism(width=30, depth=15, height=hc, segs_w=10, segs_d=5, segs_z=int(hc / 2)),
        #     RoundedCornerBox(width=30, depth=10, height=hr, corner_radius=2, segs_w=15, segs_d=5, segs_z=int(hr / 2))
        # ]

        # for i, maker in enumerate(li):
        #     h = 0 if i == 0 else (hc + hr) / 2
        #     model = maker.create()
        #     building.assemble(model, Point3(0, 0, h), Vec3(0, 0, 0))

        # self.attach(building)

        # # three cylinders with different height
        # h, r = 50, 3
        # building = Building('area6_cy0', Point3(-87, -7, 0), Vec3(-24, 0, 0))

        # for i, (x, y) in enumerate([(-r, 0), (0, r * 3 ** 0.5), (r, 0)]):
        #     height = h - i * 10
        #     maker = Cylinder(radius=r, height=height, segs_a=int(height / 2))
        #     model = maker.create()
        #     building.assemble(model, Point3(x, y, 0), Vec3(0, 0, 0))

        # self.attach(building)


        ################################
        # two corner rounded box, 3 stacked
        # building = Building('area6_rb1', Point3(-91, -48, 5), Vec3(-76, 0, 0))
        # start_w, diff = 40, 5

        # for i in range(3):
        #     w = start_w - diff * i
        #     d = 20 - diff * i
        #     h = 20 if i == 0 else 5
        #     z = 0 if i == 0 else 12.5 + h * (i - 1)
        #     x = -(diff / 2) * i
        #     y = -(diff / 2) * i

        #     model = RoundedCornerBox(
        #         width=w, depth=d, height=h, corner_radius=5, rounded_b_right=False, rounded_f_left=False
        #     ).create()
        #     building.assemble(model, Point3(x, y, z), Vec3(0, 0, 0))

        # self.attach(building)

        # # sphere dome
        # building = Building('area6_sp0', Point3(-70, -20, 0), Vec3(22, 0, 0))
        # model = Sphere(radius=15, inner_radius=13, slice_deg=170, bottom_clip=0).create()
        # building.build(model)
        # self.attach(building)

        # # 4 elliptical prism, different height
        # building = Building('area6_cy0', Point3(-67, -48, 0), Vec3(38, 0, 0))

        # for i, (x, y) in enumerate([(0, 6), (-4, 0), (4, 0), (0, -6)]):
        #     h = 45 - i * 8
        #     model = EllipticalPrism(major_axis=4, minor_axis=3, height=h, segs_a=5).create()
        #     building.assemble(model, Point3(x, y, 0), Vec3(0, 0, 0))

        # self.attach(building)

        # # sphere dome
        # building = Building('area4_sp1', Point3(-9, -99, 1), Vec3(-138, 0, 0))

        # li = [
        #     Cylinder(radius=22, height=2, segs_bottom_cap=11, segs_top_cap=11, ring_slice_deg=180),
        #     Cylinder(radius=20, height=2, segs_bottom_cap=10, segs_top_cap=10, ring_slice_deg=180),
        #     Cylinder(radius=18, height=2, segs_bottom_cap=9, segs_top_cap=9, ring_slice_deg=180),
        #     Sphere(radius=16, inner_radius=14, slice_deg=180, bottom_clip=0, segs_bottom_cap=8, segs_top_cap=8)
        # ]

        # for i, maker in enumerate(li):
        #     model = maker.create()
        #     building.assemble(model, Point3(0, -2 * i, 2 * i), Vec3(0, 0, 0))

        # self.attach(building)

        # # rounded corner box with cylinder on the top
        # building = Building('area4_rb2', Point3(-33, -63, 1), Vec3(-34, 0, 0))
        # li = [
        #     [Point3(0, 0, 10), Vec3(0, 0, 0), RoundedCornerBox(width=30, depth=20, height=18, segs_w=4, segs_d=4, segs_z=5, corner_radius=5)],
        #     [Point3(-7, 0, 18), Vec3(0, 0, 0), Cylinder(radius=7, height=6, segs_a=3, segs_bottom_cap=3, segs_top_cap=3)]
        # ]
        # for pos, hpr, maker in li:
        #     model = maker.create()
        #     building.assemble(model, pos, hpr)

        # self.attach(building)

        # # three layer cylinders
        # building = Building('area2_cy0', Point3(-42, -80, 0), Vec3(0, 0, 0))
        # args = [
        #     dict(radius=8, height=10, segs_a=5),
        #     dict(radius=6, height=20, segs_a=15),
        #     dict(radius=4, height=20, segs_a=15)
        # ]
        # self.stack_cylinder(building, args)


class Area7(City):

    def build(self):
        # ##### area7-1#####


        # building = Building('area71_0', Point3(-29, -16, 0), Vec3(0, 0, 0))
        # li = [
        #     [Point3(0, 0, 0), Cylinder(radius=22, height=2, segs_bottom_cap=11, segs_top_cap=11)],
        #     [Point3(0, 0, 2), Cylinder(radius=20, height=2, segs_bottom_cap=10, segs_top_cap=10)],
        #     [Point3(0, 0, 4), Cylinder(radius=18, height=2, segs_bottom_cap=9, segs_top_cap=9)],
        #     [Point3(0, 0, 6), Sphere(radius=16, inner_radius=14, slice_deg=180, bottom_clip=0, segs_bottom_cap=8, segs_top_cap=4)]
        # ]

        # for pos, maker in li:
        #     model = maker.create()
        #     building.assemble(model, pos, Vec3(0, 0, 0))

        # self.attach(building)

        # # triple layer capsule prism, different w, d, h
        # building = Building('area7_cp0', Point3(3, -19, 7.5), Vec3(-20, 0, 0))
        # start_w, start_d = 30, 25
        # diff = 5
        # z = 0

        # for i in range(3):
        #     h = 15 if i == 0 else 4
        #     w = start_w - diff * i
        #     d = start_d - diff * i
        #     z += (0 if i == 0 else h / 2)
        #     pos = Point3(diff / 2 * i, -diff / 2 * i, z)

        #     model = CapsulePrism(
        #         width=w, depth=d, height=h, segs_w=int(w / 2), segs_d=int(d / 2),
        #         segs_z=int(h / 2), rounded_right=False
        #     ).create()

        #     building.assemble(model, pos, Vec3(0, 0, 0))
        #     z += h / 2

        # self.attach(building)

        # # half torus
        # building = Building('area4_tr0', Point3(18, -58, 3.5), Vec3(-104, 0, 0))
        # model = Torus(ring_radius=9, section_radius=4, ring_slice_deg=180, section_slice_deg=90).create()
        # building.build(model)
        # self.attach(building)


        # double layer two rounded corner boxes, different h, w, d
        # building = Building('area7_rb0', Point3(-12, -43, 5), Vec3(-34, 0, 0))
        # diff = 5
        # z = 0

        # for i in range(2):
        #     w = 35 - diff * i
        #     d = 20 - diff * i
        #     h = 10 if i == 0 else 5
        #     z += (0 if i == 0 else h / 2)
        #     pos = Point3(-diff / 2 * i, diff / 2 * i, z)

        #     model = RoundedCornerBox(
        #         width=w, depth=d, height=h, corner_radius=d / 2, segs_w=int(w / 2), segs_d=int(d / 2),
        #         segs_z=int(h / 2), rounded_b_left=False, rounded_f_right=False
        #     ).create()

        #     building.assemble(model, pos, Vec3(0, 0, 0))
        #     z += h / 2

        # self.attach(building)


        # ##### area7-3#####

        building = Building('area71_0', Point3(56, 4, 0), Vec3(4, 0, 0))
        maker = Cylinder(radius=6, height=6, segs_a=3)
        dirs = [(0, -1), (0, 1)]
        self.stack_shifting_prisms(building, 8, maker, dirs, 4, start_z=0)




        # multi layer sylinder, different center y
        # building = Building('area7_cy0', Point3(-35, -19, 0), Vec3(4, 0, 0))
        # n, v, h = 10, 4, 6

        # for i in range(n):
        #     model = Cylinder(radius=6, height=h, segs_a=3).create()
        #     y = 0 if i == 0 or i == n - 1 else (v if i % 2 == 0 else -v)
        #     building.assemble(model, Point3(0, y, h * i), Vec3(0, 0, 0))

        # self.attach(building)

        


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
        # building = Building('area7_rb1', Point3(55, -6, 2.5), Vec3(-28, 0, 0))
        # z, h = 0, 5

        # for i in range(9):
        #     model = RoundedCornerBox(width=20, depth=20, height=5, corner_radius=5).create()
        #     angle = 0 if i % 2 == 0 else 45
        #     building.assemble(model, Point3(0, 0, z), Vec3(angle, 0, 0))
        #     z += h

        # self.attach(building)

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

        building = Building('area51_0', Point3(10, -116, 0), Vec3(44, 0, 0))
        model = Cylinder(radius=10, height=5, segs_bottom_cap=5, segs_top_cap=5).create()
        building.assemble(model, Point3(0, 0, 0), Vec3(0, 0, 0))

        args = dict(radius=10, ring_slice_deg=180, segs_bottom_cap=4, segs_top_cap=4)
        maker_1 = Cylinder(height=5, **args)
        maker_2 = Cylinder(height=0.5, segs_a=1, **args)
        self.stack_alternating_boxes(building, 14, maker_1, maker_2, start_z=5)

        # ##### area5-2 #####

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


    # building = Building('area21_0', Point3(-4, 101, 0), Vec3(0, 0, 0))
    # maker = Cylinder(radius=10, height=5)
    # z = 0
    # n = 5

    # for i in range(n):
    #     if i == 0 or i == n - 1:
    #         z += 0 if i == 0 else 5
    #         model = maker.create()
    #         building.assemble(model, Point3(0, 0, z), Vec3(0, 0, 0))
    #         continue

        
    #     for _x, _y in [(0, -1), (1, 0), (0, 1), (-1, 0)]:
    #     # for _x, _y in [(0, -1), (-1, 0)]:
    #         x = _x * 5
    #         y = _y * 5
    #         z += 5

    #         model = maker.create()
    #         building.assemble(model, Point3(x, y, z), Vec3(0, 0, 0))

        

    # self.attach(building)

    # h = 6
    #     building = Building('area21_0', Point3(-2, 105, h / 2), Vec3(-50, 0, 0))

    #     args = dict(width=26, depth=20, height=h, segs_w=13, segs_d=10, segs_z=int(h / 2)) 
    #     maker_1 = CapsulePrism(**args, rounded_left=False)
    #     maker_2 = CapsulePrism(**args, rounded_right=False)
    #     self.stack_alternating_boxes(building, 10, maker_1, maker_2)


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
            (-76, 102, 0),
            (-96, 104, 0),
            (-99, 94, 0),

            # Area2
            (36, 93, 0),
            (46, 97, 0),
            (31, 86, 0),
            (30, 79, 0),
            (-47, 60, 0),
            (-34, 59, 0),
            (-45, 74, 0),
            (-26, 104, 0),
            (-6.6, 27, 0),
            (-2, 33, 0),
            (14, 53, 0),
            # (-116, -18, 0),
            # (-118, -11, 0),
            # (-105, -20, 0),

            # Area3
            (20, 114, 0),
            (17, 121, 0),
            (114, 33, 0),
            (124, 34, 0),
            (122, 43, 0),
            (93, 13, 0),

            (123, 81, 0),
            (110, 79, 0),
            (79, 124, 0),
            (74, 111, 0),
            (78, 99, 0),

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
            (-62, -122, 0),
            (-49, -103, 0),
            (27, -117, 0),
            (30, -123, 0),

            # Area6
            (-116, -18, 0),
            (-118, -11, 0),
            (-95, -69, 0),
            (-101, -60, 0),
            (-84, -69, 0),
            (-75, -66, 0),
            (-57, -16, 0),
            (-68, -16, 0),
            (-51, -24, 0),
            (-49, -87, 0),
            (-43, -95, 0),
            (-9, -103, 0),
            (-4, -99, 0),
           

            # Area7
            # (-25, -2.5, 0),
            # (-37, -2.9, 0),
            # (20, -39, 0),
            # (21, -29, 0),
            # (69, 8, 0),
            # (61, 13, 0),
            # (82, -42, 0),
            # (49, -71, 0),

            # Area5
            # (23, -114, 0),
            # (28, -121, 0),
            # (15, -123, 0),
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
