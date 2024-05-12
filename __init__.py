from .stop_mo_addon import (
    SIMPLE_OT_stepped_interpolation,
    SIMPLE_OT_remove_stepped_interpolation,
    SIMPLE_OT_select_modified_objects,
    SIMPLE_PT_stepped_interpolation,
    register,
    unregister,
)

bl_info = {
    "name": "Stop-Mo",
    "author": "SouthernShotty",
    "version": (1, 0),
    "blender": (3, 5),
    "location": "View3D > Sidebar > Stepped Interpolation",
    "description": "Adds and removes stepped interpolation from selected objects",
    "warning": "",
    "doc_url": "",
    "category": "Animation",
}
