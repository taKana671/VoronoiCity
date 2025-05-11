import math

from panda3d.bullet import BulletRigidBodyNode
from panda3d.bullet import BulletTriangleMeshShape, BulletHeightfieldShape, ZUp
from panda3d.bullet import BulletConvexHullShape, BulletTriangleMesh, BulletConvexHullShape
from panda3d.core import NodePath, PandaNode
from panda3d.core import BitMask32, Vec3, Point3, LColor
from panda3d.core import Filename, PNMImage
from panda3d.core import GeoMipTerrain
from panda3d.core import Shader, TextureStage, TransformState
from panda3d.core import TransparencyAttrib, TexGenAttrib


from shapes.src import Plane, Cylinder, Box
from shapes.src import EllipticalPrism, RoundedCornerBox
from lights import BasicAmbientLight, BasicDayLight
from city import City

from shapes.src import Sphere


class Ground(NodePath):

    def __init__(self, w=256, d=256, segs_w=16, segs_d=16):
        super().__init__(BulletRigidBodyNode('ground'))

        plane = Plane(w, d, segs_w, segs_d)
        self.model = plane.create()
        self.model.set_texture(base.loader.load_texture('images/voronoi_region.png'))
        self.model.set_pos(0, 0, 0)
        self.model.reparent_to(self)
        self.set_tag('category', 'ground')

        mesh = BulletTriangleMesh()
        mesh.add_geom(self.model.node().get_geom(0))
        shape = BulletTriangleMeshShape(mesh, dynamic=False)
        self.node().add_shape(shape)

        self.node().set_mass(0)
        self.set_collide_mask(BitMask32.bit(1))


# class SkyBox(NodePath):

#     def __init__(self):
#         super().__init__(PandaNode('skybox'))
#         self.make_skybox()

#     def make_skybox(self):
#         self.sphere = Sphere(radius=500).create()
#         self.sphere.set_pos(0, 0, 0)
#         self.sphere.reparent_to(self)

#         ts = TextureStage.get_default()
#         self.sphere.set_tex_gen(ts, TexGenAttrib.M_world_cube_map)
#         self.sphere.set_tex_hpr(ts, (0, 180, 0))
#         self.sphere.set_tex_scale(ts, (1, -1))

#         self.sphere.set_light_off()
#         self.sphere.set_material_off()
#         imgs = base.loader.load_cube_map('images/skybox_sphere/img_#.png')
#         self.sphere.set_texture(imgs)


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

        # self.sky = SkyBox()
        # self.sky.reparent_to(self)
        # self.sky.set_pos(0, 0, 150)


    def create_city(self):
        for area in City.areas:
            a = area()
            a.build()





