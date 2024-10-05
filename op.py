import bpy
from bpy.types import Context, Object, Operator, Event, TimelineMarkers, FCurve, FModifierStepped
from bpy.props import BoolProperty


def get_user_objects():
    if bpy.context.selected_objects:
        return bpy.context.selected_objects
    elif bpy.context.active_object:
        return [bpy.context.active_object]
    else:
        return []

def is_stepped(obj: Object):
    # check should be as fast as possible
    if obj.animation_data and obj.animation_data.action:
        for fcurve in obj.animation_data.action.fcurves:
            fcurve: FCurve
            return any(mod.type == "STEPPED" for mod in fcurve.modifiers)
    return False

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

def set_stepped_interpolation(obj: Object, step_amount, offset_amount, use_frame_start, frame_start, use_frame_end, frame_end):
    for fcurve in get_fcurves(obj):
        modifiers = get_stepped_modifiers(fcurve)
        # remove unused modifiers
        if modifiers:
            remove_modifiers(fcurve, modifiers[1:])
            modifier = modifiers[0]
        else:
            modifier = fcurve.modifiers.new(type="STEPPED")
        # apply modifier settings
        modifier.mute = False
        modifier.show_expanded = True
        modifier.frame_step = step_amount
        modifier.frame_offset = offset_amount
        modifier.use_frame_start = use_frame_start
        modifier.frame_start = frame_start
        modifier.use_frame_end = use_frame_end
        modifier.frame_end = frame_end
        modifier.use_influence = False

def step_from_markers(obj, frames):
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


class STEPPED_OT_apply(Operator):
    bl_label = "Apply Steps"
    bl_idname = "stepped.apply"
    bl_description = "Apply Stepped Interpolation to selected objects or all selected and already stepped objects"
    bl_options = {"REGISTER", "UNDO"}
    update_all: BoolProperty(name="Update all stepped", default=False)  # type: ignore

    def execute(self, context: Context):
        if self.update_all:
            bpy.ops.stepped.select(keep_current=True)
        if context.scene.STEPPED_properties.preset == "MARKERS":
            self.apply_with_markers()
        else:
            self.apply_with_properties(context)
        self.report({"INFO"}, "Applying step parameters")
        return {"FINISHED"}

    def apply_with_markers(self):
        frames = [0] + [marker.frame for marker in bpy.context.scene.timeline_markers]
        frames = sorted(frames)
        for obj in get_user_objects():
            step_from_markers(obj, frames)

    def apply_with_properties(self, context: Context):
        props = context.scene.STEPPED_properties
        for obj in get_user_objects():
            set_stepped_interpolation(
                obj=obj,
                step_amount=props.step_amount,
                offset_amount=props.offset_amount,
                use_frame_start=props.use_frame_start,
                frame_start=props.frame_start,
                use_frame_end=props.use_frame_end,
                frame_end=props.frame_end,
            )


class STEPPED_OT_remove(Operator):
    bl_label = "Remove Steps"
    bl_idname = "stepped.delete"
    bl_description = "Remove Stepped Interpolation from selected objects or all objects"
    bl_options = {"REGISTER", "UNDO"}
    from_all: BoolProperty(name="Remove from all stepped", default=False)  # type: ignore

    def execute(self, context: Context):
        if self.from_all:
            bpy.ops.stepped.select()
        for obj in get_user_objects():
            fcurves = get_fcurves(obj)
            for fcurve in fcurves:
                modifiers = get_stepped_modifiers(fcurve)
                remove_modifiers(fcurve, modifiers)
        return {"FINISHED"}


class STEPPED_OT_select(Operator):
    bl_label = "Select Stepped"
    bl_idname = "stepped.select"
    bl_description = "Select all objects in the scene that have a stepped interpolation modifier"
    bl_options = {"REGISTER", "UNDO"}
    keep_current: BoolProperty(name="Keep current selection", default=False) # type: ignore

    def execute(self, context: Context):
        print(f"==>{ self.keep_current=}")
        for obj in context.scene.objects:
            obj: Object
            if is_stepped(obj):
                obj.select_set(True)
            elif not self.keep_current:
                obj.select_set(False)
        return {"FINISHED"}


class STEPPED_OT_auto_update(Operator):
    bl_label = "Auto update"
    bl_idname = "stepped.auto_update"
    bl_description = "Whenever an option changes, update all stepped objects"
    initial_markers = []
    prop = None

    def execute(self, context: Context):
        self.prop = context.scene.STEPPED_properties
        if self.prop.auto_running:
            self.prop.auto_off = True
            return self.return_finished()
        else:
            self.prop.auto_off = False
            context.window_manager.modal_handler_add(self)
            self.prop.auto_running = True
            return {"RUNNING_MODAL"}

    def modal(self, context: Context, event: Event):
        if self.prop.auto_off or self.prop.preset != "MARKERS":
            return self.return_finished()
        if self.markers_changed(context.scene.timeline_markers):
            bpy.ops.stepped.apply(update_all=True)
            self.save_markers(context)
        return {"PASS_THROUGH"}

    def return_finished(self):
        self.prop.auto_running = False
        return {"FINISHED"}

    def save_markers(self, context: Context):
        self.initial_markers = [m.frame for m in context.scene.timeline_markers]

    def markers_changed(self, markers_b: TimelineMarkers):
        if len(self.initial_markers) != len(markers_b):
            return True
        for a, b in zip(self.initial_markers, markers_b):
            if a != b.frame:
                return True
        return False
