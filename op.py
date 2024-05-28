import bpy
from bpy.types import Context, Operator, Event, TimelineMarkers, TimelineMarker
from bpy.props import BoolProperty


def get_user_objects():
    if bpy.context.selected_objects:
        return bpy.context.selected_objects
    elif bpy.context.active_object:
        return [bpy.context.active_object]
    else:
        return []


def add_or_update_stepped_interpolation(obj, step_amount, offset_amount, use_frame_start, frame_start, use_frame_end, frame_end):
    if obj.animation_data and obj.animation_data.action:
        for fcurve in obj.animation_data.action.fcurves:
            stepped_modifiers = [mod for mod in fcurve.modifiers if mod.type == "STEPPED"]
            # remove unused modifiers
            for modifier in stepped_modifiers[1:]:
                fcurve.modifiers.remove(modifier)
            # get or add needed modifier
            if stepped_modifiers:
                modifier = stepped_modifiers[0]
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


def remove_stepped_interpolation(obj):
    if obj.animation_data and obj.animation_data.action:
        for fcurve in obj.animation_data.action.fcurves:
            modifiers_to_remove = [mod for mod in fcurve.modifiers if mod.type == "STEPPED"]
            for modifier in modifiers_to_remove:
                fcurve.modifiers.remove(modifier)


def step_from_markers(obj, frames):
    if not obj.animation_data and obj.animation_data.action:
        return
    for fcurve in obj.animation_data.action.fcurves:
        modifiers = [mod for mod in fcurve.modifiers if mod.type == "STEPPED"]
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
    bl_description = "Apply Stepped Interpolation to selected objects or all stepped objects"
    bl_options = {"REGISTER", "UNDO"}
    update_all: BoolProperty(name="Update all stepped", default=False)  # type: ignore

    def execute(self, context):
        if self.update_all:
            bpy.ops.stepped.select()
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

    def apply_with_properties(self, context):
        step_amount = context.scene.STEPPED_properties.step_amount
        offset_amount = context.scene.STEPPED_properties.offset_amount
        use_frame_start = context.scene.STEPPED_properties.use_frame_start
        frame_start = context.scene.STEPPED_properties.frame_start
        use_frame_end = context.scene.STEPPED_properties.use_frame_end
        frame_end = context.scene.STEPPED_properties.frame_end
        for obj in get_user_objects():
            add_or_update_stepped_interpolation(
                obj,
                step_amount,
                offset_amount,
                use_frame_start,
                frame_start,
                use_frame_end,
                frame_end
            )


class STEPPED_OT_remove(Operator):
    bl_label = "Remove Steps"
    bl_idname = "stepped.delete"
    bl_description = "Remove Stepped Interpolation from selected objects or all objects"
    bl_options = {"REGISTER", "UNDO"}
    from_all: BoolProperty(name="remove_from_all", default=False)  # type: ignore

    def execute(self, context):
        if self.from_all:
            bpy.ops.stepped.select()
        for obj in get_user_objects():
            action = obj.animation_data.action
            if not action:
                continue
            fcurves = action.fcurves
            for fcurve in fcurves:
                for mod in fcurve.modifiers:
                    if mod.type == "STEPPED":
                        mod.frame_step = 1
            # Remove the stepped interpolation modifier
            remove_stepped_interpolation(obj)
        return {"FINISHED"}


class STEPPED_OT_select(Operator):
    bl_label = "Select Stepped"
    bl_idname = "stepped.select"
    bl_description = "Select all objects in the scene that have a stepped interpolation modifier"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        modified_objects = []
        for obj in bpy.context.scene.objects:
            if obj.animation_data and obj.animation_data.action:
                for fcurve in obj.animation_data.action.fcurves:
                    if any(mod.type == "STEPPED" for mod in fcurve.modifiers):
                        modified_objects.append(obj)
        bpy.ops.object.select_all(action="DESELECT")
        for obj in modified_objects:
            obj.select_set(True)
        return {"FINISHED"}


class STEPPED_OT_auto_update(Operator):
    bl_label = "Auto update"
    bl_idname = "stepped.auto_update"
    bl_description = "Whenever an option changes, update all stepped objects"
    initial_markers = []
    prop = None

    def execute(self, context: Context):
        self.prop = bpy.context.scene.STEPPED_properties
        if self.prop.auto_running:
            self.prop.auto_off = True
            return self.return_finished()
        else:
            self.prop.auto_off = False
            context.window_manager.modal_handler_add(self)
            self.prop.auto_running = True
            return {"RUNNING_MODAL"}

    def modal(self, context: Context, event: Event): #TODO check also if parameters changed
        if self.markers_changed(context.scene.timeline_markers):
            bpy.ops.stepped.apply(update_all=True)
            self.save_markers(context)
        if event.type in ["RIGHTMOUSE"]:  # TODO debug
            return self.return_finished()
        if self.prop.auto_off:
            return self.return_finished()
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