import sys
from enum import Enum, auto

from direct.showbase.ShowBase import ShowBase
from direct.showbase.ShowBaseGlobal import globalClock
from direct.showbase.InputStateGlobal import inputState
from direct.interval.IntervalGlobal import Sequence, Func
from panda3d.bullet import BulletWorld, BulletDebugNode
from panda3d.bullet import BulletSphereShape
from panda3d.core import Point3, Vec3, Vec2, BitMask32
from panda3d.core import NodePath
from panda3d.core import AntialiasAttrib, TransparencyAttrib
from panda3d.core import load_prc_file_data

from scene import Scene
from viewer import Viewer, Motions


load_prc_file_data("", """
    textures-power-2 none
    gl-coordinate-system default
    window-title Panda3D Voronoi City
    filled-wireframe-apply-shader true
    stm-max-views 8
    stm-max-chunk-count 2048
    framebuffer-multisample 1
    multisamples 2""")


# If set to True, the clicked building can be moved or rotated.
# See below if statement in __init__.
UNDER_CONSTRUCTION = False


class Status(Enum):

    SCREEN_CHANGE = auto()
    WAITING = auto()
    ACTIVE = auto()


class View(Enum):

    SKY = auto()
    GROUND = auto()


class VoronoiCity(ShowBase):

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

        self.test_shape = BulletSphereShape(0.25)
        self.sky_pos = Point3(0, -300, 200)
        self.ground_pos = Point3(13, -89, 2)

        self.sky_view_root = NodePath('sky_view_root')
        self.sky_view_root.set_pos_hpr(Point3(0, 0, 0), Vec3(140, 0, -0.9))

        self.viewer = Viewer()
        self.view_from_sky(self.sky_pos, 40)
        self.viewer.reparent_to(self.render)
        self.world.attach(self.viewer.node())
        self.camera.reparent_to(self.viewer)

        self.clicked = False
        self.dragging = False
        self.before_mouse_pos = None
        self.target = None
        self.screen_changed = False
        self.status = Status.ACTIVE
        self.view = View.SKY

        self.accept('escape', sys.exit)
        self.accept('mouse1', self.mouse_click)
        self.accept('mouse1-up', self.mouse_release)
        self.accept('t', self.toggle_debug)
        self.accept('i', self.get_target_info)
        self.accept('r', self.release_target)
        self.accept('v', self.toggle_view)
        self.accept('w', self.toggle_wireframe)

        # viewer control
        inputState.watch_with_modifiers(Motions.FORWARD, 'arrow_up')
        inputState.watch_with_modifiers(Motions.BACKWARD, 'arrow_down')
        inputState.watch_with_modifiers(Motions.LEFT, 'arrow_left')
        inputState.watch_with_modifiers(Motions.RIGHT, 'arrow_right')
        inputState.watch_with_modifiers(Motions.DOWN, 'd')
        inputState.watch_with_modifiers(Motions.UP, 'u')

        if UNDER_CONSTRUCTION:
            self.accept('x', self.positioning, ['x', 1])
            self.accept('shift-x', self.positioning, ['x', -1])
            self.accept('y', self.positioning, ['y', 1])
            self.accept('shift-y', self.positioning, ['y', -1])
            self.accept('z', self.positioning, ['z', 1])
            self.accept('shift-z', self.positioning, ['z', -1])
            self.accept('h', self.positioning, ['h', 1])
            self.accept('shift-h', self.positioning, ['h', -1])

        self.taskMgr.add(self.update, 'update')

    def toggle_view(self):
        self.status = Status.SCREEN_CHANGE

    def fade_camera(self, parent, pos, look_at, view_func, fov=40, duration=2.0):
        self.screen_changed = False

        props = self.win.get_properties()
        size = props.get_size()
        buffer = self.win.make_texture_buffer('tex_buffer', *size)
        buffer.set_clear_color_active(True)
        buffer.set_clear_color((0.5, 0.5, 0.5, 1.0))

        temp_cam = self.make_camera(buffer)
        temp_cam.node().get_lens().set_fov(fov)
        temp_cam.set_pos(pos)
        temp_cam.look_at(look_at)
        temp_cam.reparent_to(parent)

        card = buffer.get_texture_card()
        card.reparent_to(self.render2d)
        card.set_transparency(TransparencyAttrib.M_alpha)
        # card.set_transparency(TransparencyAttrib.M_multisample)

        Sequence(
            card.colorScaleInterval(duration, 1, 0, blendType='easeInOut'),
            Func(view_func, pos, fov),
            Func(card.remove_node),
            Func(self.graphicsEngine.remove_window, buffer),
            Func(self.end_fade)
        ).start()

    def view_while_moving(self, pos, fov):
        self.viewer.set_pos_hpr(pos, Vec3(0, 0, 0))
        self.camera.set_pos(Point3(0, 0, 0))
        # must call look_at after calling set_pos.
        self.camera.look_at(self.viewer)
        self.camLens.set_fov(fov)
        self.camLens.set_near_far(0.1, 1000000)

    def view_from_sky(self, pos, fov):
        self.viewer.set_pos_hpr(Point3(0, 0, 0), Vec3(140, 0, -0.9))
        self.camera.set_pos(pos)
        self.camera.look_at(Point3(0, 0, 0))
        self.camLens.set_fov(fov)
        self.camLens.set_near_far(0.1, 1000000)

    def end_fade(self):
        self.screen_changed = True

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

    def release_target(self):
        if self.target:
            self.target = None

    def get_target_info(self):
        if self.target:
            print(f'pos: {self.target.get_pos()}, hpr: {self.target.get_hpr()}')

    def positioning(self, key, direction):
        if self.target:
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
            self.viewer.set_hpr(self.viewer.get_hpr() + angle)

        self.before_mouse_pos = Vec2(mouse_pos.xy)

    def watch_keyboard(self):
        direction = Vec3()

        if inputState.is_set(Motions.FORWARD):
            direction.y += 1

        if inputState.is_set(Motions.BACKWARD):
            direction.y -= 1

        if inputState.is_set(Motions.LEFT):
            direction.x += 1

        if inputState.is_set(Motions.RIGHT):
            direction.x -= 1

        if inputState.is_set(Motions.UP):
            direction.z += 1

        if inputState.is_set(Motions.DOWN):
            direction.z -= 1

        return direction

    def change_screen(self):

        match self.view:

            case View.SKY:
                parent = self.render
                pos = self.ground_pos
                look_at = self.ground_pos
                func = self.view_while_moving
                fov = 90

            case View.GROUND:
                parent = self.sky_view_root
                pos = self.sky_pos
                look_at = Point3(0, 0, 0)
                func = self.view_from_sky
                fov = 40

        self.fade_camera(parent, pos, look_at, func, fov)

    def control(self, dt):
        if self.view == View.GROUND:
            direction = self.watch_keyboard()
            self.viewer.control(direction, dt)

        if self.mouseWatcherNode.has_mouse():
            mouse_pos = self.mouseWatcherNode.get_mouse()

            if self.clicked:
                self.click(mouse_pos)
                self.clicked = False

            if self.view == View.SKY and self.dragging:
                if globalClock.get_frame_time() - self.dragging_start_time >= 0.2:
                    self.rotate_camera(mouse_pos, dt)

    def update(self, task):
        dt = globalClock.get_dt()

        match self.status:

            case Status.SCREEN_CHANGE:
                self.change_screen()
                self.status = Status.WAITING

            case Status.WAITING:
                if self.screen_changed:
                    self.view = View.GROUND if self.view == View.SKY else View.SKY
                    self.status = Status.ACTIVE

            case Status.ACTIVE:
                self.control(dt)

        self.world.do_physics(dt)
        return task.cont


if __name__ == '__main__':
    app = VoronoiCity()
    app.run()