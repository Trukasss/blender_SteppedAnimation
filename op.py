import bpy
from bpy.types import Context, Object, Operator, Event, TimelineMarkers, FCurve, FModifierStepped
from bpy.props import BoolProperty
from . import modifiers


def get_user_objects():
    if bpy.context.selected_objects:
        return bpy.context.selected_objects
    elif bpy.context.active_object:
        return [bpy.context.active_object]
    else:
        return []


class STEPPED_OT_apply_abstract(Operator):
    bl_label = ""
    bl_idname = "stepped.apply_abstract"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context: Context):
        objs = get_user_objects()
        if context.scene.STEPPED_properties.preset == "MARKERS":
            modifiers.step_with_markers(objs)
            self.report({"INFO"}, f"Applying step from markers to {len(objs)} objects")
        else:
            modifiers.step_with_properties(objs)
            self.report({"INFO"}, f"Applying step parameters to {len(objs)} objects")
        return {"FINISHED"}


class STEPPED_OT_apply_selected(STEPPED_OT_apply_abstract):
    bl_label = "Apply Steps to selected"
    bl_idname = "stepped.apply_selected"
    bl_description = "Apply stepped interpolation to selected objects"


class STEPPED_OT_apply_all(STEPPED_OT_apply_abstract):
    bl_label = "Apply Steps and update all"
    bl_idname = "stepped.apply_all"
    bl_description = "Apply stepped interpolation to selected objects and update all stepped objects"

    def execute(self, context: Context):
        modifiers.select_stepped(keep_current=True)
        return super().execute(context)


class STEPPED_OT_remove_abstract(Operator):
    bl_label = ""
    bl_idname = "stepped.delete_abstract"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context: Context):
        for obj in get_user_objects():
            fcurves = modifiers.get_fcurves(obj)
            for fcurve in fcurves:
                stepped_modifiers = modifiers.get_stepped_modifiers(fcurve)
                modifiers.remove_modifiers(fcurve, stepped_modifiers)
        return {"FINISHED"}


class STEPPED_OT_remove_selected(STEPPED_OT_remove_abstract):
    bl_label = "Remove Steps from selected"
    bl_idname = "stepped.delete_selected"
    bl_description = "Remove stepped interpolation from selected objects"


class STEPPED_OT_remove_all(STEPPED_OT_remove_abstract):
    bl_label = "Remove all Steps"
    bl_idname = "stepped.delete_all"
    bl_description = "Remove stepped interpolation from all objects"

    def execute(self, context: Context):
        modifiers.select_stepped(keep_current=False)
        return super().execute(context)


class STEPPED_OT_select(Operator):
    bl_label = "Select Stepped"
    bl_idname = "stepped.select"
    bl_description = "Select all objects in the scene that have a stepped interpolation modifier"
    bl_options = {"REGISTER", "UNDO"}
    keep_current: BoolProperty(name="Keep current selection", default=False)  # type: ignore

    def execute(self, context: Context):
        modifiers.select_stepped()
        return {"FINISHED"}


class STEPPED_OT_auto_update(Operator):
    bl_label = "Auto update"
    bl_idname = "stepped.auto_update"
    bl_description = "Whenever a marker is moved, update all stepped objects"
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
            bpy.ops.stepped.apply_all()
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
