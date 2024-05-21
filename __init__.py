import importlib
import bpy
from bpy.props import PointerProperty

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

from . import props
importlib.reload(props)
from . import op
importlib.reload(op)
from . import ui
importlib.reload(ui)
from . import gizmo
importlib.reload(gizmo)

from .props import STEPPED_properties
from .op import STEPPED_OT_apply, STEPPED_OT_remove, STEPPED_OT_select
from .ui import STEPPED_PT_pannel
from .gizmo import STEPPED_GGT_marker, STEPPED_GT_marker_shape#, STEPPED_OT_update_marker

CLASSES = (
    STEPPED_properties,
    STEPPED_OT_apply,
    STEPPED_OT_remove,
    STEPPED_OT_select,
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