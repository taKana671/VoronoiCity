from shapes.src import Cylinder
from shapes.src import EllipticalPrism
from shapes.src import Capsule
from shapes.src import CapsulePrism
from shapes.src import RoundedCornerBox
from shapes.src import Sphere
from shapes.src import Torus


class MaterialCylinder(Cylinder):

    def __init__(self, radius, height, inner_radius=0, segs_c=40, ring_slice_deg=0):
        super().__init__(
            radius=radius,
            inner_radius=inner_radius,
            height=height,
            segs_c=segs_c,
            ring_slice_deg=ring_slice_deg,
            segs_a=int(height / 2) if height >= 3 else 1,
            segs_top_cap=int((radius - inner_radius) / 2),
            segs_bottom_cap=int((radius - inner_radius) / 2)
        )

        self.is_convex = not (inner_radius and ring_slice_deg)


class MaterialEllipticalPrism(EllipticalPrism):

    def __init__(self, major_axis, minor_axis, height, thickness=0.,
                 segs_c=40, ring_slice_deg=0):
        super().__init__(
            major_axis=major_axis,
            minor_axis=minor_axis,
            thickness=thickness,
            height=height,
            segs_c=segs_c,
            segs_a=int(height / 2) if height >= 3 else 1,
            segs_top_cap=int(minor_axis / 2),
            segs_bottom_cap=int(minor_axis / 2),
            ring_slice_deg=ring_slice_deg
        )

        self.is_convex = True


class MaterialCapsule(Capsule):

    def __init__(self, radius=1., inner_radius=0., height=1., segs_c=40,
                 top_hemisphere=True, bottom_hemisphere=True, ring_slice_deg=0):
        super().__init__(
            radius=radius,
            inner_radius=inner_radius,
            height=height,
            segs_c=segs_c,
            segs_a=int(height / 2) if height >= 3 else 1,
            segs_top_cap=int((radius - inner_radius) / 2),
            segs_bottom_cap=int((radius - inner_radius) / 2),
            top_hemisphere=top_hemisphere,
            bottom_hemisphere=bottom_hemisphere,
            ring_slice_deg=ring_slice_deg
        )

        self.is_convex = not (inner_radius and ring_slice_deg)


class MaterialCapsulePrism(CapsulePrism):

    def __init__(self, width, depth, height, thickness=0., rounded_left=True,
                 rounded_right=True, open_top=False, open_bottom=False):
        super().__init__(
            width=width,
            depth=depth,
            height=height,
            segs_w=int(width / 2) if width >= 3 else 1,
            segs_d=int(depth / 2) if depth >= 3 else 1,
            segs_z=int(height / 2) if height >= 3 else 1,
            thickness=thickness,
            rounded_left=rounded_left,
            rounded_right=rounded_right,
            open_top=open_top,
            open_bottom=open_bottom
        )

        self.is_convex = True


class MaterialRoundedCornerBox(RoundedCornerBox):

    def __init__(self, width=2., depth=2., height=2., thickness=0., open_top=False,
                 open_bottom=False, corner_radius=0.5, rounded_f_left=True, rounded_f_right=True,
                 rounded_b_left=True, rounded_b_right=True):
        super().__init__(
            width=width,
            depth=depth,
            height=height,
            segs_w=int(width / 2) if width >= 3 else 1,
            segs_d=int(depth / 2) if depth >= 3 else 1,
            segs_z=int(height / 2) if height >= 3 else 1,
            thickness=thickness,
            open_top=open_top,
            open_bottom=open_bottom,
            corner_radius=corner_radius,
            rounded_f_left=rounded_f_left,
            rounded_f_right=rounded_f_right,
            rounded_b_left=rounded_b_left,
            rounded_b_right=rounded_b_right
        )

        self.is_convex = True


class MaterialSphere(Sphere):

    def __init__(self, radius, inner_radius=0, segs_h=40, segs_v=40, segs_bottom_cap=2,
                 segs_top_cap=2, slice_deg=0, bottom_clip=-1., top_clip=1):

        segs_cap = int(radius * 2 / 2) if radius * 2 >= 3 else 1
        super().__init__(
            radius=radius,
            inner_radius=inner_radius,
            segs_h=segs_h,
            segs_v=segs_v,
            segs_bottom_cap=segs_cap,
            segs_top_cap=segs_cap,
            slice_deg=slice_deg,
            bottom_clip=bottom_clip,
            top_clip=top_clip
        )

        self.is_convex = False


class MaterialTorus(Torus):

    def __init__(self, ring_radius=1., section_radius=.5, ring_slice_deg=0, section_slice_deg=0):
        super().__init__(
            ring_radius=ring_radius,
            section_radius=section_radius,
            ring_slice_deg=ring_slice_deg,
            section_slice_deg=section_slice_deg
        )

        self.is_convex = False
