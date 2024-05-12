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

import bpy
from bpy.types import PropertyGroup
from bpy.props import FloatProperty, IntProperty



def add_or_update_stepped_interpolation(obj, step_amount, offset_amount, start_frame, end_frame):
    if obj.animation_data and obj.animation_data.action:
        for fcurve in obj.animation_data.action.fcurves:
            stepped_modifiers = [mod for mod in fcurve.modifiers if mod.type == 'STEPPED']

            if stepped_modifiers:
                for modifier in stepped_modifiers:
                    modifier.frame_step = step_amount
                    modifier.frame_offset = offset_amount
                    modifier.use_influence = True
                    modifier.use_frame_start = True
                    modifier.use_frame_end = True
                    modifier.frame_start = start_frame
                    modifier.frame_end = end_frame
            else:
                modifier = fcurve.modifiers.new(type='STEPPED')
                modifier.frame_step = step_amount
                modifier.frame_offset = offset_amount
                modifier.use_influence = True
                modifier.use_frame_start = True
                modifier.use_frame_end = True
                modifier.frame_start = start_frame
                modifier.frame_end = end_frame

def remove_stepped_interpolation(obj):
    if obj.animation_data and obj.animation_data.action:
        for fcurve in obj.animation_data.action.fcurves:
            modifiers_to_remove = [mod for mod in fcurve.modifiers if mod.type == 'STEPPED']
            for modifier in modifiers_to_remove:
                fcurve.modifiers.remove(modifier)

class STEPPED_OT_apply(bpy.types.Operator):
    bl_idname = "stepped.apply"
    bl_label = "Apply Steps"
    bl_description = "Apply Stepped Interpolation to Selected Objects"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        step_amount = context.scene.STEPPED_properties.step_amount
        offset_amount = context.scene.STEPPED_properties.offset_amount
        start_frame = context.scene.STEPPED_properties.start_frame
        end_frame = context.scene.STEPPED_properties.end_frame

        for obj in bpy.context.selected_objects:
            add_or_update_stepped_interpolation(obj, step_amount, offset_amount, start_frame, end_frame)
        return {'FINISHED'}

class STEPPED_OT_delete(bpy.types.Operator):
    bl_idname = "stepped.delete"
    bl_label = "Remove Steps"
    bl_description = "Remove Stepped Interpolation from Selected Objects and Deselect Them"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        for obj in bpy.context.selected_objects:
            # Set the frame step of the stepped interpolation modifier to 1
            fcurves = obj.animation_data.action.fcurves
            for fcurve in fcurves:
                for mod in fcurve.modifiers:
                    if mod.type == 'STEPPED':
                        mod.frame_step = 1

            # Remove the stepped interpolation modifier
            remove_stepped_interpolation(obj)

        bpy.ops.object.select_all(action='DESELECT')
        return {'FINISHED'}

class STEPPED_OT_select(bpy.types.Operator):
    bl_idname = "stepped.select"
    bl_label = "Select Objects"
    bl_description = "Select all objects in the scene that have a stepped interpolation modifier"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        modified_objects = []

        for obj in bpy.context.scene.objects:
            if obj.animation_data and obj.animation_data.action:
                for fcurve in obj.animation_data.action.fcurves:
                    if any(mod.type == 'STEPPED' for mod in fcurve.modifiers):
                        modified_objects.append(obj)

        bpy.ops.object.select_all(action='DESELECT')
        for obj in modified_objects:
            obj.select_set(True)

        return {'FINISHED'}

class STEPPED_PT_pannel(bpy.types.Panel):
    bl_label = "Stop-Mo"
    bl_idname = "STEPPED_PT_pannel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Stop-Mo'

    def draw(self, context):
        layout = self.layout
        scene = context.scene

        # Add the top 3 buttons in a box with 'Add/Remove Modifiers' label
        box = layout.box()
        col = box.column(align=True)
        col.label(text="Add/Remove Modifiers:")
        col.operator(STEPPED_OT_apply.bl_idname)
        col.operator(STEPPED_OT_delete.bl_idname)
        col.operator(STEPPED_OT_select.bl_idname)

        # Add the middle 3 number fields in a box with 'Controls' label
        box = layout.box()
        col = box.column(align=True)
        col.label(text="Controls:")
        col.prop(scene.STEPPED_properties, "step_amount", text="Step Amount")
        col.prop(scene.STEPPED_properties, "offset_amount", text="Offset Amount")
        col.prop(scene.STEPPED_properties, "start_frame", text="Start Frame")
        col.prop(scene.STEPPED_properties, "end_frame", text="End Frame")

class STEPPED_properties(PropertyGroup):
    step_amount: IntProperty(name="Step Amount", default=1, min=0, max=100) # type: ignore
    offset_amount: IntProperty(name="Offset Amount", default=1, min=0, max=100) # type: ignore
    start_frame: IntProperty(name="Start Frame", default=0, min=0, max=10000) # type: ignore
    end_frame: IntProperty(name="End Frame", default=100, min=0, max=10000) # type: ignore

def register():
    bpy.utils.register_class(STEPPED_OT_apply)
    bpy.utils.register_class(STEPPED_OT_delete)
    bpy.utils.register_class(STEPPED_OT_select)
    bpy.utils.register_class(STEPPED_PT_pannel)
    bpy.utils.register_class(STEPPED_properties)

    bpy.types.Scene.STEPPED_properties = PointerProperty(type=STEPPED_properties)

def unregister():
    bpy.utils.unregister_class(STEPPED_OT_apply)
    bpy.utils.unregister_class(STEPPED_OT_delete)
    bpy.utils.unregister_class(STEPPED_OT_select)
    bpy.utils.unregister_class(STEPPED_PT_pannel)
    bpy.utils.unregister_class(STEPPED_properties)

    del bpy.types.Scene.STEPPED_properties