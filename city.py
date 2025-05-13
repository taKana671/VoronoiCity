import random
from enum import Enum

from panda3d.bullet import BulletRigidBodyNode
from panda3d.bullet import BulletTriangleMeshShape, BulletTriangleMesh
from panda3d.bullet import BulletConvexHullShape, BulletCylinderShape, ZUp
from panda3d.core import NodePath
from panda3d.core import BitMask32, Vec3, Point3, LColor
from panda3d.core import TransformState


from building_materials import MaterialCylinder as Cylinder
from building_materials import MaterialEllipticalPrism as EllipticalPrism
from building_materials import MaterialCapsule as Capsule
from building_materials import MaterialCapsulePrism as CapsulePrism
from building_materials import MaterialRoundedCornerBox as RoundedBox
from building_materials import MaterialSphere as Sphere
from building_materials import MaterialTorus as Torus


class Color(Enum):

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

    def add_collision_shape(self, model, is_convex):
        if is_convex:
            shape = BulletConvexHullShape()
            shape.add_geom(model.node().get_geom(0))
        else:
            mesh = BulletTriangleMesh()
            mesh.add_geom(model.node().get_geom(0))
            shape = BulletTriangleMeshShape(mesh, dynamic=False)

        return shape

    def build(self, maker, is_convex=True):
        model = maker.create()
        shape = self.add_collision_shape(model, maker.is_convex)
        self.node().add_shape(shape)
        model.reparent_to(self)

    def assemble(self, maker, pos, hpr, is_convex=True):
        model = maker.create()
        shape = self.add_collision_shape(model, maker.is_convex)
        self.node().add_shape(shape, TransformState.make_pos_hpr(pos, hpr))
        model.set_pos_hpr(pos, hpr)
        model.reparent_to(self)


class PineTree(NodePath):

    def __init__(self, model, name, scale=1.5):
        super().__init__(BulletRigidBodyNode(f'tree_{name}'))
        tree = model.copy_to(self)
        tree.set_transform(TransformState.make_pos(Vec3(0, 0, -4)))
        tree.reparent_to(self)

        end, tip = tree.get_tight_bounds()
        height = (tip - end).z
        shape = BulletCylinderShape(0.5, height, ZUp)
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

    def plant_trees(self, *pos_xy):
        model = base.loader.load_model('models/pinetree/tree2.bam')
        area = self.__class__.__name__.lower()

        for i, (x, y) in enumerate(pos_xy):
            tree = PineTree(model, f'{area}_{i}')
            tree.set_pos(Point3(x, y, 6))
            self.attach(tree)

    def assemble(self, building, makers, attach=True):
        for pos, hpr, maker in makers:
            building.assemble(maker, pos, hpr)

        if attach:
            self.attach(building)

    def stack_shifting_boxes(self, building, n, maker, dirs, shift, start_z=0):
        """dirs: [(0, -1), (1, 0), (0, 1), (-1, 0)]
        """
        z = 0

        for i in range(n):
            if i == 0:
                z += start_z
                building.assemble(maker, Point3(0, 0, z), Vec3(0, 0, 0))
                continue

            for _x, _y in dirs:
                x = _x * shift
                y = _y * shift
                z += maker.height / 2

                building.assemble(maker, Point3(x, y, z), Vec3(0, 0, 0))
                z += maker.height / 2

        self.attach(building)

    def stack_alternating_box_center(self, building, n, maker_1, maker_2, dir_x=0, dir_y=0,
                                     shift_x=0, shift_y=0, start_x=0, start_y=0, start_z=0):
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
            building.assemble(maker, Point3(x, y, z), Vec3(0, 0, 0))
            z += maker.height / 2

        self.attach(building)

    def stack_alternating_boxes(self, building, n, maker_1, maker_2, x=0, y=0, start_z=0, h=0, attach=True):
        z = 0

        for i in range(n):
            maker = maker_1 if i % 2 == 0 else maker_2
            z += start_z if i == 0 else maker.height / 2
            building.assemble(maker, Point3(x, y, z), Vec3(h, 0, 0))
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
                building.assemble(maker, Point3(0, 0, z), Vec3(0, 0, 0))
                continue

            for _x, _y in dirs:
                x = _x * shift
                y = _y * shift
                z += maker.height

                building.assemble(maker, Point3(x, y, z), Vec3(0, 0, 0))

        self.attach(building)

    def stack_alternating_prisms(self, building, n, maker_1, maker_2, x=0, y=0, z=0, h=0, attach=True):

        for i in range(n):
            maker = maker_1 if i % 2 == 0 else maker_2
            building.assemble(maker, Point3(x, y, z), Vec3(h, 0, 0), maker.is_convex)
            z += maker.height

        if attach:
            self.attach(building)

    def stack_rotating_prisms(self, building, maker, n, angles, x=0, y=0, z=0, attach=True):
        z = 0

        for _ in range(n):
            for angle in angles:
                building.assemble(maker, Point3(x, y, z), Vec3(angle, 0, 0))
                z += maker.height

        if attach:
            self.attach(building)

    def stack_rotating_boxes(self, building, maker, n, angles, x=0, y=0, start_z=0, attach=True):
        z = 0
        i = 0

        for _ in range(n):
            for angle in angles:
                z += start_z if i == 0 else maker.height / 2
                building.assemble(maker, Point3(x, y, z), Vec3(angle, 0, 0))
                z += maker.height / 2
                i += 1

        if attach:
            self.attach(building)


class Area1(City):

    def build(self):
        # ##### area1-2 #####

        building = Building('area12_0', Point3(-105, 120, 0), Vec3(0, 0, 0))
        maker_1 = Cylinder(radius=7, height=6)
        maker_2 = Cylinder(radius=5, height=0.5)
        self.stack_alternating_prisms(building, 15, maker_1, maker_2)

        # ##### area1-4 #####

        building = Building('area14_0', Point3(-121, 85, 3), Vec3(90, 0, 0))
        args = dict(corner_radius=4, rounded_f_left=False, rounded_f_right=False)
        maker_1 = RoundedBox(width=30, depth=10, height=6, **args)
        maker_2 = RoundedBox(width=28, depth=8, height=0.5, **args)
        self.stack_alternating_boxes(building, 11, maker_1, maker_2)

        # ##### area1-5 #####

        building = Building('area15_0', Point3(-112, 42, 3), Vec3(66, 0, 0))

        args = dict(corner_radius=4)
        maker_1 = RoundedBox(width=40, depth=17, height=6, **args)
        maker_2 = RoundedBox(width=38, depth=15, height=0.5, **args)
        self.stack_alternating_boxes(building, 9, maker_1, maker_2, attach=False)

        maker = CapsulePrism(width=6, depth=12, height=17, rounded_right=False)
        building.assemble(maker, Point3(0, 0, 30), Vec3(90, 0, 90))
        self.attach(building)

        # ##### area1-3 #####

        building = Building('area13_0', Point3(-78, 81, 2.5), Vec3(-28, 0, 0))
        args = dict(width=40, height=5, corner_radius=5)
        maker_1 = RoundedBox(depth=20, **args)
        maker_2 = RoundedBox(depth=15, **args)
        shift_y = (maker_1.depth - maker_2.depth) * 0.5
        self.stack_alternating_box_center(building, 4, maker_1, maker_2, dir_y=1, shift_y=shift_y)

        building = Building('area13_1', Point3(-54, 108, 3), Vec3(64, 0, 0))
        args = dict(width=10, height=6)
        maker_1 = CapsulePrism(depth=30, **args)
        maker_2 = CapsulePrism(depth=25, **args)
        shift_y = (maker_1.depth - maker_2.depth) * 0.5
        self.stack_alternating_box_center(building, 8, maker_1, maker_2, dir_y=1, shift_y=shift_y)

        # ##### trees #####

        self.plant_trees(
            (-126, 121), (-124, 125), (-115, 13), (-119, 5), (-124, -3),
            (-82, 118), (-88, 111), (-95, 104), (-100, 97), (-76, 124)
        )


class Area2(City):

    def build(self):
        # ##### area2-1 #####

        building = Building('area21_0', Point3(-6, 115, 2.5), Vec3(90, 0, 0))
        maker = RoundedBox(width=15, depth=15, height=5, corner_radius=4)
        dirs = [(0, -1), (0, 1)]
        self.stack_shifting_prisms(building, 8, maker, dirs, 5, start_z=0)

        building = Building('area21_1', Point3(-3, 84, 2.5), Vec3(14, 0, 0))
        args_1 = dict(height=5, rounded_right=False)
        args_2 = dict(height=0.5, rounded_right=False)

        maker_1 = CapsulePrism(width=40, depth=30, **args_1)
        maker_2 = CapsulePrism(width=38, depth=28, **args_2)
        self.stack_alternating_boxes(building, 3, maker_1, maker_2, attach=False)

        maker_1 = CapsulePrism(width=18, depth=28, **args_2)
        maker_2 = CapsulePrism(width=20, depth=30, **args_1)
        self.stack_alternating_boxes(building, 2, maker_1, maker_2, x=10, start_z=8)

        # ##### area2-2 #####

        building = Building('area22_0', Point3(57, 69, 2.5), Vec3(-42, 0, 0))
        args = dict(corner_radius=10, rounded_f_left=False)

        maker_1 = RoundedBox(width=40, depth=42, height=5, **args)
        maker_2 = RoundedBox(width=38, depth=40, height=0.5, **args)
        self.stack_alternating_boxes(building, 3, maker_1, maker_2, attach=False)

        maker_1 = RoundedBox(width=30, depth=32, height=5, **args)
        maker_2 = RoundedBox(width=28, depth=30, height=0.5, **args)
        self.stack_alternating_boxes(building, 3, maker_1, maker_2, start_z=11, x=-5, y=5)

        # ##### area2-3 #####

        building = Building('area23_0', Point3(-27, 33, 2.5), Vec3(-80, 0, 0))
        args = dict(corner_radius=8, rounded_b_right=False, rounded_f_left=False)

        maker_1 = RoundedBox(width=34, depth=28, height=5, **args)
        maker_2 = RoundedBox(width=32, depth=26, height=0.5, **args)
        self.stack_alternating_boxes(building, 3, maker_1, maker_2, attach=False)

        maker_1 = RoundedBox(width=28, depth=22, height=0.5, **args)
        maker_2 = RoundedBox(width=30, depth=24, height=5, **args)
        self.stack_alternating_boxes(building, 2, maker_1, maker_2, start_z=8, x=2, y=2, attach=False)

        maker_1 = RoundedBox(width=24, depth=18, height=0.5, **args)
        maker_2 = RoundedBox(width=26, depth=20, height=5, **args)
        self.stack_alternating_boxes(building, 2, maker_1, maker_2, start_z=13.5, x=4, y=4)

        building = Building('area23_1', Point3(-1.8, 47, 2.5), Vec3(6, 0, 0))
        args = dict(corner_radius=5, rounded_b_right=False)
        maker_1 = RoundedBox(width=20, depth=15, height=5, **args)
        maker_2 = RoundedBox(width=18, depth=13, height=0.5, **args)
        self.stack_alternating_boxes(building, 10, maker_1, maker_2)

        # ##### area2-4 #####

        building = Building('area24_0', Point3(25, 22, 2.5), Vec3(52, 0, 0))
        args = dict(corner_radius=8)

        maker_1 = RoundedBox(width=44, depth=30, height=5, **args)
        maker_2 = RoundedBox(width=43, depth=22, height=0.5, **args)
        self.stack_alternating_boxes(building, 3, maker_1, maker_2, attach=False)

        maker_1 = RoundedBox(width=36, depth=22, height=5, **args)
        maker_2 = RoundedBox(width=34, depth=20, height=0.5, **args)
        self.stack_alternating_boxes(building, 3, maker_1, maker_2, start_z=10.5)

        # ##### trees #####

        self.plant_trees(
            (36, 93), (46, 97), (31, 86), (30, 79), (-6.6, 27),
            (-2, 33), (-45, 73), (-49, 65), (-31, 58), (-41, 56),
            (-49, 57)
        )


class Area3(City):

    def build(self):
        # ##### area3-1 #####

        building = Building('area31_0', Point3(41, 116, 0), Vec3(0, 0, 0))
        maker_1 = EllipticalPrism(major_axis=20, minor_axis=11, height=5)
        maker_2 = EllipticalPrism(major_axis=18, minor_axis=9, height=0.5)
        self.stack_alternating_prisms(building, 15, maker_1, maker_2)

        # ##### area3-2 #####

        building = Building('area32_0', Point3(104, 103, 2.5), Vec3(0, 0, 0))
        args = dict(height=5, corner_radius=5)
        maker_1 = RoundedBox(**args, width=30, depth=30)
        maker_2 = RoundedBox(**args, width=20, depth=20)
        self.stack_alternating_boxes(building, 13, maker_1, maker_2)

        # ##### area3-3 #####

        building = Building('area33_0', Point3(96, 44, 1), Vec3(46, 0, 0))
        li = [
            [Point3(0, 0, 0), Vec3(0, 0, 0), CapsulePrism(width=30, depth=30, height=2)],
            [Point3(0, 0, 2), Vec3(0, 0, 0), CapsulePrism(width=25, depth=25, height=2)],
        ]

        for pos, hpr, maker in li:
            building.assemble(maker, pos, hpr)

        maker_1 = CapsulePrism(width=20, depth=20, height=5)
        maker_2 = CapsulePrism(width=18, depth=18, height=0.5)
        self.stack_alternating_boxes(building, 17, maker_1, maker_2)

        building = Building('area7_rb1', Point3(113, 16, 2.5), Vec3(-28, 0, 0))
        maker = RoundedBox(width=10, depth=10, height=5, corner_radius=2)
        self.stack_rotating_boxes(building, maker, 6, [0, 45])

        # ##### trees #####

        self.plant_trees(
            (20, 114), (17, 121), (116, 1.5), (106, 1.4), (98, 4.7),
            (88, 92), (112, 2.5), (115, -13), (118, -9.9), (124, -6.5),
            (122, 2.4), (123, 81), (110, 79), (79, 124), (74, 111),
            (78, 99)
        )


class Area4(City):

    def build(self):
        # ##### area4-1 #####

        building = Building('area41_0', Point3(-120, -66, 2.5), Vec3(90, 0, 0))
        args = dict(rounded_f_left=False, rounded_f_right=False)
        maker = RoundedBox(width=50, depth=15, height=5, corner_radius=5, **args)
        building.assemble(maker, Point3(0, 0, 0), Vec3(0, 0, 0))

        args = dict(**args, corner_radius=3)
        maker_1 = RoundedBox(width=50, depth=10, height=5, **args)
        maker_2 = RoundedBox(width=48, depth=8, height=0.5, **args)
        self.stack_alternating_boxes(building, 12, maker_1, maker_2, start_z=5, y=2)

        # ##### area4-2 #####

        building = Building('area42_0', Point3(-78, -101, 0), Vec3(0, 0, 0))
        li = [
            [Point3(0, 0, 0), Cylinder(radius=22, height=2)],
            [Point3(0, 0, 2), Cylinder(radius=20, height=2)],
            [Point3(0, 0, 4), Cylinder(radius=18, height=2)],
            [Point3(0, 0, 6), Sphere(radius=16, inner_radius=14, slice_deg=120, bottom_clip=0)]
        ]

        for pos, maker in li:
            building.assemble(maker, pos, Vec3(0, 0, 0))

        self.attach(building)

        building = Building('area42_1', Point3(-49, -118, 0), Vec3(4, 0, 0))
        diff = 0.2

        for i in range(12):
            maker = EllipticalPrism(
                major_axis=10 - i * diff,
                minor_axis=8 - i * diff,
                height=5
            )
            building.assemble(maker, Point3(0, 0, 5 * i), Vec3(0, 0, 0))

        self.attach(building)

        # ##### trees #####

        self.plant_trees(
            (-17, -126), (-24, -126), (-120, -125), (-113, -125), (-116, -96),
            (-126, -101), (-118, -36), (-122, -32), (-110, -111), (-110, -102),
            (-106, -95), (-100, -89), (27, -117), (30, -123)
        )


class Area6(City):

    def build(self):
        # ##### area6-1 #####

        building = Building('area61_0', Point3(-101, -2, 2.5), Vec3(0, 0, 0))
        maker = RoundedBox(width=20, depth=20, height=5, corner_radius=2)
        dirs = [(0, -1), (-1, 0)]
        self.stack_shifting_boxes(building, 6, maker, dirs, 5)

        building = Building('area61_1', Point3(-75, 21, 1), Vec3(-72, 0, 0))
        args = dict(height=2)

        li = [
            [Point3(0, 0, 0), Vec3(0, 0, 0), CapsulePrism(width=22, depth=34, **args)],
            [Point3(0, 0, 2), Vec3(0, 0, 0), CapsulePrism(width=21, depth=29.5, **args)],
            [Point3(0, 0, 4), Vec3(0, 0, 0), CapsulePrism(width=20, depth=25, **args)],
            [Point3(9, 2, 5), Vec3(0, 0, -90), Capsule(radius=12, inner_radius=10, height=18, ring_slice_deg=270)]
        ]

        for pos, hpr, maker in li:
            building.assemble(maker, pos, hpr)

        self.attach(building)

        # ##### area6-2 #####

        building = Building('area62_0', Point3(-72, -40, 0), Vec3(82, 0, 0))
        args = dict(ring_slice_deg=120)
        maker_1 = Cylinder(radius=18, inner_radius=13, height=5, **args)
        maker_2 = Cylinder(radius=17, inner_radius=14, height=0.5, **args)
        self.stack_alternating_prisms(building, 5, maker_1, maker_2, attach=False)

        args = dict(ring_slice_deg=90)
        maker_1 = Cylinder(radius=15, inner_radius=10, height=5, **args)
        maker_2 = Cylinder(radius=14, inner_radius=11, height=0.5, **args)
        self.stack_alternating_prisms(building, 15, maker_1, maker_2, x=-5, y=18, h=180)

        # ##### area6-3 #####

        building = Building('area63_0', Point3(-25, -99, 2.5), Vec3(-54, 0, 0))
        maker = RoundedBox(width=18, depth=18, height=5, corner_radius=4)
        self.stack_rotating_boxes(building, maker, 6, [0, 45])

        building = Building('area63_1', Point3(-24, -69, 2.5), Vec3(-34, 0, 0))
        args_1 = dict(height=5, rounded_left=False)
        args_2 = dict(height=0.5, rounded_left=False)

        maker_1 = CapsulePrism(width=55, depth=15, **args_1)
        maker_2 = CapsulePrism(width=52, depth=12, **args_2)
        self.stack_alternating_boxes(building, 5, maker_1, maker_2, attach=False)

        maker_1 = CapsulePrism(width=10, depth=15, **args_1)
        maker_2 = CapsulePrism(width=8, depth=12, **args_2)
        self.stack_alternating_boxes(building, 5, maker_1, maker_2, h=-90, x=-20, y=-12.5)

        # ##### trees #####

        self.plant_trees(
            (-116, -18), (-118, -11), (-95, -69), (-101, -60), (-84, -69),
            (-75, -66), (-57, -16), (-68, -16), (-51, -24), (-49, -87),
            (-43, -95), (-9, -103), (-4, -99), (-69, 50), (-76, 54),
            (-83, 54), (-88, 50)
        )


class Area7(City):

    def build(self):
        # ##### area7-1#####

        building = Building('area71_0', Point3(-21, -34, 1.5), Vec3(0, 0, 0))
        maker = Torus(ring_radius=6, section_radius=3, section_slice_deg=90)
        building.build(maker)
        self.attach(building)

        building = Building('area71_1', Point3(-13, -14, 2.5), Vec3(-12, 0, 0))
        args = dict(corner_radius=5, rounded_b_right=False)
        maker_1 = RoundedBox(width=60, depth=15, height=5, **args)
        maker_2 = RoundedBox(width=48, depth=12, height=0.5, **args)
        self.stack_alternating_boxes(building, 5, maker_1, maker_2, attach=False)

        args = dict(corner_radius=5, rounded_f_right=False, rounded_f_left=False, rounded_b_right=False)
        maker_1 = RoundedBox(width=15, depth=36, height=5, **args)
        maker_2 = RoundedBox(width=12, depth=18, height=0.5, **args)
        self.stack_alternating_boxes(building, 5, maker_1, maker_2, x=22.5, y=-25.5, attach=False)

        args = dict(ring_slice_deg=180)
        maker_1 = Cylinder(radius=10, height=5, **args)
        maker_2 = Cylinder(radius=3, height=0.5, **args)
        self.stack_alternating_boxes(building, 9, maker_1, maker_2, x=30, y=-33.5, start_z=-2.5, h=90)

        # ##### area7-3#####

        building = Building('area73_0', Point3(50, -7, 0), Vec3(22, 0, 0))
        maker = Cylinder(radius=6, height=6)
        dirs = [(0, -1), (0, 1)]
        self.stack_shifting_prisms(building, 8, maker, dirs, 4, start_z=0)

        building = Building('area73_1', Point3(83, -13, 2.5), Vec3(-34, 0, 0))
        maker_1 = CapsulePrism(width=10, depth=26, height=5)
        maker_2 = CapsulePrism(width=8, depth=24, height=0.5)
        self.stack_alternating_boxes(building, 3, maker_1, maker_2, attach=False)

        maker_1 = Cylinder(radius=11, height=0.5)
        maker_2 = Cylinder(radius=13, height=5)
        self.stack_alternating_boxes(building, 4, maker_1, maker_2, start_z=5.5, x=5)

        # ##### area7-2#####

        building = Building('area72_0', Point3(34, -49, 0), Vec3(84, 0, 0))
        args = dict(segs_c=4, ring_slice_deg=180)
        maker_1 = Cylinder(radius=20, inner_radius=10, height=5, **args)
        maker_2 = Cylinder(radius=18, inner_radius=16, height=0.5, **args)
        self.stack_alternating_prisms(building, 9, maker_1, maker_2)

        building = Building('area72_1', Point3(74, -54, 2.5), Vec3(-98, 0, 0))
        args = dict(corner_radius=8, rounded_b_right=False, rounded_f_left=False)

        maker_1 = RoundedBox(width=26, depth=28, height=5, **args)
        maker_2 = RoundedBox(width=24, depth=26, height=0.5, **args)
        self.stack_alternating_boxes(building, 3, maker_1, maker_2, attach=False)

        maker_1 = RoundedBox(width=18, depth=20, height=0.5, **args)
        maker_2 = RoundedBox(width=20, depth=22, height=5, **args)
        self.stack_alternating_boxes(building, 2, maker_1, maker_2, start_z=8)

        # ##### trees #####

        self.plant_trees(
            (-40, -26), (-36, -34), (-18, -50), (-11, -55), (51, 9),
            (56, 12), (63, 13), (71, 10), (51, -29), (60, -31),
            (67, -34), (74, -36), (47, -74), (54, -74), (64, -74),
        )


class Area5(City):

    def build(self):
        # ##### area5-1 #####

        building = Building('area51_0', Point3(10, -116, 0), Vec3(44, 0, 0))
        maker = Cylinder(radius=10, height=5)
        building.assemble(maker, Point3(0, 0, 0), Vec3(0, 0, 0))

        args = dict(radius=10, ring_slice_deg=180)
        maker_1 = Cylinder(height=5, **args)
        maker_2 = Cylinder(height=0.5, **args)
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
        maker_1 = RoundedBox(width=20, depth=15, height=5, **args)
        maker_2 = RoundedBox(width=18, depth=13, height=0.5, **args)
        self.stack_alternating_boxes(building, 13, maker_1, maker_2)

        # ##### area5-3 #####

        building = Building('area53_0', Point3(103, -113, 2.5), Vec3(-18, 0, 0))
        args = dict(width=25, depth=20, height=5, corner_radius=10)
        maker_1 = RoundedBox(**args, rounded_f_left=False, rounded_b_right=False)
        maker_2 = RoundedBox(**args, rounded_f_right=False, rounded_b_left=False)
        self.stack_alternating_boxes(building, 10, maker_1, maker_2)

        building = Building('area53_1', Point3(85, -86, 1.5), Vec3(26, 0, 0))
        maker = Torus(ring_radius=9, section_radius=4, section_slice_deg=90, ring_slice_deg=180)
        building.build(maker)
        self.attach(building)

        # ##### area5-4 #####

        building = Building('area54_0', Point3(119, -77, 0), Vec3(196, 0, 0))
        maker_1 = Cylinder(radius=8, height=5)
        maker_2 = Cylinder(radius=6, height=0.5)
        self.stack_alternating_prisms(building, 16, maker_1, maker_2)

        # ##### area5-5 #####

        building = Building('area55_0', Point3(119, -39, 2.5), Vec3(90, 0, 0))

        maker_1 = RoundedBox(width=40, depth=15, height=5, corner_radius=4)
        maker_2 = RoundedBox(width=38, depth=12, height=0.5, corner_radius=4)
        self.stack_alternating_boxes(building, 9, maker_1, maker_2, attach=False)

        maker = CapsulePrism(width=6, depth=12, height=15, rounded_right=False)
        building.assemble(maker, Point3(0, 0, 25), Vec3(90, 0, 90))
        self.attach(building)

        # ##### trees #####

        self.plant_trees(
            (115, -14), (122, -8), (123, -91), (125, -98), (104, -97),
            (79, -104), (82, -116), (37, -112), (41, -121)
        )