from panda3d.core import AmbientLight, DirectionalLight
from panda3d.core import NodePath, PandaNode
from panda3d.core import Vec3, Point3


class BasicAmbientLight(NodePath):

    def __init__(self):
        super().__init__(AmbientLight('ambient_light'))
        self.node().set_color((0.6, 0.6, 0.6, 1))
        self.reparent_to(base.render)
        base.render.set_light(self)


class BasicDayLight(NodePath):

    def __init__(self):
        super().__init__(DirectionalLight('directional_light'))
        self.node().get_lens().set_film_size(200, 200)
        self.node().get_lens().set_near_far(10, 200)
        self.node().set_color((1, 1, 1, 1))
        self.set_pos_hpr(Point3(0, 0, 100), Vec3(-30, -60, 0))

        self.node().set_shadow_caster(True, 8192, 8192)
        # self.node().set_shadow_caster(True, 4096, 4096)

        state = self.node().get_initial_state()
        temp = NodePath(PandaNode('temp_np'))
        temp.set_state(state)
        temp.set_depth_offset(-5)
        # temp.set_depth_offset(-2)
        self.node().set_initial_state(temp.get_state())

        base.render.set_light(self)
        base.render.set_shader_auto()
        self.reparent_to(base.render)
        # self.node().show_frustum()