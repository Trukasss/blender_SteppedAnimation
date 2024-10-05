from bpy.types import Panel
from .op import (
    STEPPED_OT_select,
    STEPPED_OT_apply_selected,
    STEPPED_OT_apply_all,
    STEPPED_OT_remove_selected,
    STEPPED_OT_remove_all,
    STEPPED_OT_auto_update,
)


class STEPPED_PT_pannel(Panel):
    bl_label = "Stepped addon"
    bl_idname = "STEPPED_PT_pannel"
    bl_space_type = "DOPESHEET_EDITOR"
    bl_region_type = "UI"
    bl_category = "Stepped"

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        props = scene.STEPPED_properties

        # Add the middle 3 number fields in a box with "Controls" label
        col = layout.column(align=False)
        col.label(text="Modifier Controls")
        row = col.row(align=True)
        row.prop(props, "preset", expand=True)
        box = col.box()
        if props.preset == "PARAMETERS":
            box.prop(props, "step_amount", text="Step Amount")
            box.prop(props, "offset_amount", text="Offset Amount")
            row = box.row()
            row.prop(props, "use_frame_start", text="")
            sub_row = row.row()
            sub_row.prop(props, "frame_start", text="Start Frame")
            sub_row.active = props.use_frame_start
            row = box.row()
            row.prop(props, "use_frame_end", text="")
            sub_row = row.row()
            sub_row.prop(props, "frame_end", text="End Frame")
            sub_row.active = props.use_frame_end
        else:  # preset markers
            if props.auto_running:
                box.operator(STEPPED_OT_auto_update.bl_idname, text="Auto update: ON", icon="SEQUENCE_COLOR_01")
            else:
                box.operator(STEPPED_OT_auto_update.bl_idname, text="Auto update: OFF")

        # Add the top 3 buttons in a box with "Add/Remove Modifiers" label
        col = layout.column(align=True)
        col.label(text="Add / Remove Modifiers")
        col.operator(STEPPED_OT_apply_selected.bl_idname, text="Step")
        col.operator(STEPPED_OT_apply_all.bl_idname, text="Step All")
        col.operator(STEPPED_OT_remove_selected.bl_idname, text="Unstep")
        col.operator(STEPPED_OT_remove_all.bl_idname, text="Unstep All")
        col.label(text="Select")
        col.operator(STEPPED_OT_select.bl_idname)
