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

# Function to add or update Stepped Interpolation F-Curve Modifier to an object
def add_or_update_stepped_interpolation(obj, step_amount, start_frame, end_frame):
    if obj.animation_data and obj.animation_data.action:
        for fcurve in obj.animation_data.action.fcurves:
            stepped_modifiers = [mod for mod in fcurve.modifiers if mod.type == 'STEPPED']

            if stepped_modifiers:
                for modifier in stepped_modifiers:
                    modifier.frame_step = step_amount
                    modifier.use_influence = True
                    modifier.use_frame_start = True
                    modifier.use_frame_end = True
                    modifier.frame_start = start_frame
                    modifier.frame_end = end_frame
            else:
                modifier = fcurve.modifiers.new(type='STEPPED')
                modifier.frame_step = step_amount
                modifier.use_influence = True
                modifier.use_frame_start = True
                modifier.use_frame_end = True
                modifier.frame_start = start_frame
                modifier.frame_end = end_frame

# Function to remove Stepped Interpolation F-Curve Modifier from an object
def remove_stepped_interpolation(obj):
    if obj.animation_data and obj.animation_data.action:
        for fcurve in obj.animation_data.action.fcurves:
            modifiers_to_remove = [mod for mod in fcurve.modifiers if mod.type == 'STEPPED']
            for modifier in modifiers_to_remove:
                fcurve.modifiers.remove(modifier)

class SIMPLE_OT_stepped_interpolation(bpy.types.Operator):
    bl_idname = "simple.stepped_interpolation"
    bl_label = "Apply Steps"
    bl_description = "Apply Stepped Interpolation to Selected Objects"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        step_amount = context.scene.step_amount
        start_frame = context.scene.start_frame
        end_frame = context.scene.end_frame

        for obj in bpy.context.selected_objects:
            add_or_update_stepped_interpolation(obj, step_amount, start_frame, end_frame)
        return {'FINISHED'}

class SIMPLE_OT_remove_stepped_interpolation(bpy.types.Operator):
    bl_idname = "simple.remove_stepped_interpolation"
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

class SIMPLE_OT_select_modified_objects(bpy.types.Operator):
    bl_idname = "simple.select_modified_objects"
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

import math

class SIMPLE_OT_add_animation(bpy.types.Operator):
    bl_idname = "simple.add_animation"
    bl_label = "Add Animation"
    bl_description = "Add Animation to the Z Rotation of the Selected Mapping Node"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        obj = context.active_object
        if not obj:
            return {'CANCELLED'}

        material = obj.active_material
        if not material:
            return {'CANCELLED'}

        node_tree = material.node_tree
        if not node_tree:
            return {'CANCELLED'}

        node = node_tree.nodes.active

        if node and node.type == 'MAPPING':
            z_rotation = node.inputs['Rotation'].default_value

            for i, value in enumerate([0, 90, 180, 270, 0]):
                frame = context.scene.frame_current + (i * 6)
                z_rotation[2] = math.radians(value)
                node.inputs['Rotation'].keyframe_insert(data_path='default_value', frame=frame, index=2)

            if node.id_data.animation_data and node.id_data.animation_data.action:
                for fcurve in node.id_data.animation_data.action.fcurves:
                    if fcurve.data_path == "nodes[\"" + node.name + "\"].inputs[1].default_value":
                        modifier = fcurve.modifiers.new(type='CYCLES')
        return {'FINISHED'}

class SIMPLE_OT_step_loop(bpy.types.Operator):
    bl_idname = "simple.step_loop"
    bl_label = "Step/Loop"
    bl_description = "Set interpolation to constant and add cyclic F-modifier for selected keyframes"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        # Iterate through all actions
        for action in bpy.data.actions:
            for fcurve in action.fcurves:
                # Check if any keyframes in the fcurve are selected
                selected_keyframes = [kf for kf in fcurve.keyframe_points if kf.select_control_point]

                # Set interpolation type to constant for selected keyframes
                for kf in selected_keyframes:
                    kf.interpolation = 'CONSTANT'

                # Add cyclic F-modifier if there are selected keyframes in the fcurve
                if selected_keyframes:
                    cyclic_modifier_exists = False
                    for mod in fcurve.modifiers:
                        if mod.type == 'CYCLES':
                            cyclic_modifier_exists = True
                            break

                    if not cyclic_modifier_exists:
                        fcurve.modifiers.new(type='CYCLES')

        return {'FINISHED'}

class SIMPLE_PT_stepped_interpolation(bpy.types.Panel):
    bl_label = "Stop-Mo"
    bl_idname = "SIMPLE_PT_stepped_interpolation"
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
        col.operator(SIMPLE_OT_stepped_interpolation.bl_idname)
        col.operator(SIMPLE_OT_remove_stepped_interpolation.bl_idname)
        col.operator(SIMPLE_OT_select_modified_objects.bl_idname)

        # Add the middle 3 number fields in a box with 'Controls' label
        box = layout.box()
        col = box.column(align=True)
        col.label(text="Controls:")
        col.prop(scene, "step_amount", text="Step Amount")
        col.prop(scene, "start_frame", text="Start Frame")
        col.prop(scene, "end_frame", text="End Frame")
        
        # Add the bottom 2 number fields in a box with 'Aniamte Texture' label
        box = layout.box()
        col = box.column(align=True)
        col.label(text="Animate Texture")
        col.operator(SIMPLE_OT_add_animation.bl_idname, text="Add Animation")
        col.operator(SIMPLE_OT_step_loop.bl_idname, text="Step/Loop")

def register():
    bpy.utils.register_class(SIMPLE_OT_stepped_interpolation)
    bpy.utils.register_class(SIMPLE_OT_remove_stepped_interpolation)
    bpy.utils.register_class(SIMPLE_OT_select_modified_objects)
    bpy.utils.register_class(SIMPLE_PT_stepped_interpolation)
    bpy.utils.register_class(SIMPLE_OT_add_animation)
    bpy.utils.register_class(SIMPLE_OT_step_loop)

    bpy.types.Scene.step_amount = bpy.props.FloatProperty(name="Step Amount", default=1.0, min=0.0, max=100.0)
    bpy.types.Scene.start_frame = bpy.props.FloatProperty(name="Start Frame", default=0.0, min=0.0, max=10000.0)
    bpy.types.Scene.end_frame = bpy.props.FloatProperty(name="End Frame", default=100.0, min=0.0, max=10000.0)

def unregister():
    bpy.utils.unregister_class(SIMPLE_OT_stepped_interpolation)
    bpy.utils.unregister_class(SIMPLE_OT_remove_stepped_interpolation)
    bpy.utils.unregister_class(SIMPLE_OT_select_modified_objects)
    bpy.utils.unregister_class(SIMPLE_PT_stepped_interpolation)
    bpy.utils.unregister_class(SIMPLE_OT_add_animation)
    bpy.utils.unregister_class(SIMPLE_OT_step_loop)

    del bpy.types.Scene.step_amount
    del bpy.types.Scene.start_frame
    del bpy.types.Scene.end_frame