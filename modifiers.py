import bpy
from bpy.types import Context, Object, Operator, Event, TimelineMarkers, FCurve, FModifierStepped
from bpy.props import BoolProperty


def is_stepped(obj: Object):
    # check should be as fast as possible
    if obj.animation_data and obj.animation_data.action:
        for fcurve in obj.animation_data.action.fcurves:
            fcurve: FCurve
            return any(mod.type == "STEPPED" for mod in fcurve.modifiers)
    return False


def select_stepped(keep_current=False):
    for obj in bpy.context.scene.objects:
        obj: Object
        if is_stepped(obj):
            obj.select_set(True)
        elif not keep_current:
            obj.select_set(False)


def get_fcurves(obj: Object) -> list[FCurve]:
    if not obj.animation_data or not obj.animation_data.action:
        return []
    return obj.animation_data.action.fcurves


def get_stepped_modifiers(fcurve: FCurve) -> list[FModifierStepped]:
    return [mod for mod in fcurve.modifiers if mod.type == "STEPPED"]


def remove_modifiers(fcurve: FCurve, modifiers: list[FModifierStepped]):
    for modifier in modifiers:
        modifier.frame_step = 1
        fcurve.modifiers.remove(modifier)


def step_with_properties(objs: list[Object]):
    props = bpy.context.scene.STEPPED_properties
    for obj in objs:
        for fcurve in get_fcurves(obj):
            modifiers = get_stepped_modifiers(fcurve)
            if modifiers: # remove all but first stepped modifier
                remove_modifiers(fcurve, modifiers[1:])
                modifier = modifiers[0]
            else:
                modifier = fcurve.modifiers.new(type="STEPPED")
            modifier.mute = False
            modifier.show_expanded = True
            modifier.frame_step = props.step_amount
            modifier.frame_offset = props.offset_amount
            modifier.use_frame_start = props.use_frame_start
            modifier.frame_start = props.frame_start
            modifier.use_frame_end = props.use_frame_end
            modifier.frame_end = props.frame_end
            modifier.use_influence = False


def step_with_markers(objs: list[Object]):
    frames = [0] + [marker.frame for marker in bpy.context.scene.timeline_markers]
    frames = sorted(frames)
    for obj in objs:
        for fcurve in get_fcurves(obj):
            modifiers = get_stepped_modifiers(fcurve)
            for i, frame in enumerate(frames):
                # get or add needed modifier
                if i < len(modifiers):
                    modifier = modifiers[i]
                else:
                    modifier = fcurve.modifiers.new(type="STEPPED")
                # apply modifier settings
                modifier.mute = False
                modifier.show_expanded = False
                modifier.frame_step = 100000
                modifier.frame_offset = frame
                modifier.use_frame_start = True
                modifier.frame_start = frame
                modifier.frame_step = 100000
                if i + 1 < len(frames):
                    modifier.use_frame_end = True
                    modifier.frame_end = frames[i + 1] - 0.001
                else:
                    modifier.use_frame_end = False
                modifier.use_influence = False
            # remove unused modifiers
            if len(modifiers) > len(frames):
                for modifier in modifiers[len(frames):]:
                    fcurve.modifiers.remove(modifier)
