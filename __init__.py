import importlib

from . import stop_mo_addon
importlib.reload(stop_mo_addon)

from .stop_mo_addon import (
    STEPPED_OT_apply,
    STEPPED_OT_remove,
    STEPPED_OT_select,
    STEPPED_PT_pannel,
    register,
    unregister,
)

bl_info = {
    "name": "Stop-Mo",
    "author": "Lukas Sabaliauskas",
    "version": (1, 0),
    "blender": (3, 5),
    "description": "Adds and removes stepped interpolation from selected objects",
    "warning": "",
    "doc_url": "",
    "category": "Animation",
}
