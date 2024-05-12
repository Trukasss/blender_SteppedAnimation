import bpy
from bpy.types import PropertyGroup
from bpy.props import PointerProperty, IntProperty, EnumProperty, BoolProperty

def get_objs():
    if bpy.context.selected_objects:
        return bpy.context.selected_objects
    elif bpy.context.active_object:
        return [bpy.context.active_object]
    return []

def add_or_update_stepped_interpolation(obj, step_amount, offset_amount, use_frame_start, frame_start, use_frame_end, frame_end):
    if obj.animation_data and obj.animation_data.action:
        for fcurve in obj.animation_data.action.fcurves:
            stepped_modifiers = [mod for mod in fcurve.modifiers if mod.type == 'STEPPED']
            # remove unused modifiers
            for modifier in stepped_modifiers[1:]:
                fcurve.modifiers.remove(modifier)
            # get or add needed modifier
            if stepped_modifiers:
                modifier = stepped_modifiers[0]
            else:
                modifier = fcurve.modifiers.new(type='STEPPED')
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
            modifiers_to_remove = [mod for mod in fcurve.modifiers if mod.type == 'STEPPED']
            for modifier in modifiers_to_remove:
                fcurve.modifiers.remove(modifier)

def step_from_markers(obj, frames):
    if not obj.animation_data and obj.animation_data.action:
        return
    for fcurve in obj.animation_data.action.fcurves:
        modifiers = [mod for mod in fcurve.modifiers if mod.type == 'STEPPED']
        for i, frame in enumerate(frames):
            # get or add needed modifier
            if i < len(modifiers):
                modifier = modifiers[i]
            else:
                modifier = fcurve.modifiers.new(type='STEPPED')
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

class STEPPED_OT_apply(bpy.types.Operator):
    bl_idname = "stepped.apply"
    bl_label = "Apply Steps"
    bl_description = "Apply Stepped Interpolation to Selected Objects"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        if context.scene.STEPPED_properties.preset == "MARKERS":
            self.apply_with_markers()
        else:
            self.apply_with_properties(context)
        return {'FINISHED'}
    
    def apply_with_markers(self):
        frames = [0] + [marker.frame for marker in bpy.context.scene.timeline_markers]
        frames = sorted(frames)
        for obj in get_objs():
            step_from_markers(obj, frames)

    def apply_with_properties(self, context):
        step_amount = context.scene.STEPPED_properties.step_amount
        offset_amount = context.scene.STEPPED_properties.offset_amount
        use_frame_start = context.scene.STEPPED_properties.use_frame_start
        frame_start = context.scene.STEPPED_properties.frame_start
        use_frame_end = context.scene.STEPPED_properties.use_frame_end
        frame_end = context.scene.STEPPED_properties.frame_end
        for obj in get_objs():
            add_or_update_stepped_interpolation(
                obj, 
                step_amount, 
                offset_amount,
                use_frame_start,
                frame_start, 
                use_frame_end,
                frame_end
                )

class STEPPED_OT_remove(bpy.types.Operator):
    bl_idname = "stepped.delete"
    bl_label = "Remove Steps"
    bl_description = "Remove Stepped Interpolation from Selected Objects"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        for obj in get_objs():
            # Set the frame step of the stepped interpolation modifier to 1
            fcurves = obj.animation_data.action.fcurves
            for fcurve in fcurves:
                for mod in fcurve.modifiers:
                    if mod.type == 'STEPPED':
                        mod.frame_step = 1

            # Remove the stepped interpolation modifier
            remove_stepped_interpolation(obj)
        return {'FINISHED'}

class STEPPED_OT_select(bpy.types.Operator):
    bl_idname = "stepped.select"
    bl_label = "Select Stepped"
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
    bl_space_type = 'GRAPH_EDITOR'
    bl_region_type = 'UI'
    bl_category = 'Stop-Mo'

    def draw(self, context):
        layout = self.layout
        scene = context.scene

        # Selection
        col = layout.column(align=True)
        col.label(text="Object Selection")
        box = col.box()
        box_col = box.column(align=True)
        for obj in get_objs():
            box_col.label(text=obj.name)
        col.operator(STEPPED_OT_select.bl_idname)

        # Add the middle 3 number fields in a box with 'Controls' label
        col = layout.column(align=False)
        col.label(text="Modifier Controls")
        row = col.row(align=True)
        row.prop(scene.STEPPED_properties, "preset", expand=True)
        if context.scene.STEPPED_properties.preset == "PARAMETERS":
            box = col.box()
            box.prop(scene.STEPPED_properties, "step_amount", text="Step Amount")
            box.prop(scene.STEPPED_properties, "offset_amount", text="Offset Amount")
            row = box.row()
            row.prop(scene.STEPPED_properties, "use_frame_start", text="")
            sub_row = row.row()
            sub_row.prop(scene.STEPPED_properties, "frame_start", text="Start Frame")
            sub_row.active = context.scene.STEPPED_properties.use_frame_start
            row = box.row()
            row.prop(scene.STEPPED_properties, "use_frame_end", text="")
            sub_row = row.row()
            sub_row.prop(scene.STEPPED_properties, "frame_end", text="End Frame")
            sub_row.active = context.scene.STEPPED_properties.use_frame_end

        # Add the top 3 buttons in a box with 'Add/Remove Modifiers' label
        col = layout.column(align=True)
        col.label(text="Add/Remove Modifiers")
        col.operator(STEPPED_OT_apply.bl_idname)
        col.operator(STEPPED_OT_remove.bl_idname)

class STEPPED_properties(PropertyGroup):
    step_amount: IntProperty(name="Step Amount", default=2, min=0, max=100) # type: ignore
    offset_amount: IntProperty(name="Offset Amount", default=1, min=0, max=100) # type: ignore
    frame_start: IntProperty(name="Start Frame", default=1, min=0, max=10000) # type: ignore
    use_frame_start: BoolProperty(name="Use Start Frame", default=False) # type: ignore
    frame_end: IntProperty(name="End Frame", default=250, min=0, max=10000) # type: ignore
    use_frame_end: BoolProperty(name="Use End Frame", default=False) # type: ignore
    preset: EnumProperty(
        name="Presets",
        description="Apply stepped interpolation from classic parameters or based on timeline markers.",
        items=[
            ("PARAMETERS", "Parameters", "Use parameters"),
            ("MARKERS", "Markers", "Use markers"),
            ],
        ) # type: ignore

def register():
    bpy.utils.register_class(STEPPED_OT_apply)
    bpy.utils.register_class(STEPPED_OT_remove)
    bpy.utils.register_class(STEPPED_OT_select)
    bpy.utils.register_class(STEPPED_PT_pannel)
    bpy.utils.register_class(STEPPED_properties)

    bpy.types.Scene.STEPPED_properties = PointerProperty(type=STEPPED_properties)

def unregister():
    bpy.utils.unregister_class(STEPPED_OT_apply)
    bpy.utils.unregister_class(STEPPED_OT_remove)
    bpy.utils.unregister_class(STEPPED_OT_select)
    bpy.utils.unregister_class(STEPPED_PT_pannel)
    bpy.utils.unregister_class(STEPPED_properties)

    del bpy.types.Scene.STEPPED_properties