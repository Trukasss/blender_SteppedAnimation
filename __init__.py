from bpy.props import PointerProperty
import bpy
import importlib
from . import props
from . import modifiers
from . import op
from . import ui
from . import gizmo

from .props import (
    STEPPED_properties,
)
from .op import (
    STEPPED_OT_apply_abstract,
    STEPPED_OT_apply_selected,
    STEPPED_OT_apply_all,
    STEPPED_OT_remove_abstract,
    STEPPED_OT_remove_selected,
    STEPPED_OT_remove_all,
    STEPPED_OT_select,
    STEPPED_OT_auto_update,
)
from .ui import(
    STEPPED_PT_pannel,
)
from .gizmo import (
    STEPPED_GGT_marker, 
    STEPPED_GT_marker_shape,
)


bl_info = {
    "name": "Stepped",
    "author": "Lukas Sabaliauskas",
    "version": (1, 0),
    "blender": (3, 5),
    "description": "Adds and removes stepped interpolation from selected objects",
    "warning": "",
    "doc_url": "",
    "category": "Animation",
}


importlib.reload(props)
importlib.reload(modifiers)
importlib.reload(op)
importlib.reload(ui)
importlib.reload(gizmo)


CLASSES = (
    STEPPED_properties,
    STEPPED_OT_apply_abstract,
    STEPPED_OT_apply_selected,
    STEPPED_OT_apply_all,
    STEPPED_OT_remove_abstract,
    STEPPED_OT_remove_selected,
    STEPPED_OT_remove_all,
    STEPPED_OT_select,
    STEPPED_OT_auto_update,
    STEPPED_PT_pannel,
    STEPPED_GGT_marker,
    STEPPED_GT_marker_shape,
)


def register():
    for cls in CLASSES:
        bpy.utils.register_class(cls)
    bpy.types.Scene.STEPPED_properties = PointerProperty(type=STEPPED_properties)


def unregister():
    for cls in reversed(CLASSES):
        bpy.utils.unregister_class(cls)
    del bpy.types.Scene.STEPPED_properties
