import bpy
from bpy.types import PropertyGroup
from bpy.props import IntProperty, EnumProperty, BoolProperty


def apply_all(self, context):
    bpy.ops.stepped.apply(update_all=True)
    return None


class STEPPED_properties(PropertyGroup):
    step_amount: IntProperty(name="Step Amount", default=2, min=0, max=100, update=apply_all)  # type: ignore
    offset_amount: IntProperty(name="Offset Amount", default=1, min=0, max=100, update=apply_all)  # type: ignore
    frame_start: IntProperty(name="Start Frame", default=1, min=0, max=10000, update=apply_all)  # type: ignore
    use_frame_start: BoolProperty(name="Use Start Frame", default=False, update=apply_all)  # type: ignore
    frame_end: IntProperty(name="End Frame", default=250, min=0, max=10000, update=apply_all)  # type: ignore
    use_frame_end: BoolProperty(name="Use End Frame", default=False, update=apply_all)  # type: ignore
    preset: EnumProperty(
        name="Presets",
        description="Apply stepped interpolation from classic parameters or based on timeline markers.",
        items=[
            ("PARAMETERS", "Parameters", "Use parameters"),
            ("MARKERS", "Markers", "Use markers"),
        ],
    )  # type: ignore
    auto_running: BoolProperty(
        name="Auto Update",
        description="Update all stepped objects whenether the parameters or markers change",
        default=False
    )  # type: ignore
    auto_off: BoolProperty(name="Turning auto update off", default=False)  # type: ignore
