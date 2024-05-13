from bpy.types import Panel
from .op import STEPPED_OT_select, STEPPED_OT_apply, STEPPED_OT_remove, get_objs



class STEPPED_PT_pannel(Panel):
    bl_label = "Stop-Mo"
    bl_idname = "STEPPED_PT_pannel"
    bl_space_type = 'GRAPH_EDITOR'
    bl_region_type = 'UI'
    bl_category = 'Stop-Mo'

    def draw(self, context):
        layout = self.layout
        scene = context.scene

        #TODO delete this section, replace by having operator "Apply all Stepped" and "Remove all stepped"
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