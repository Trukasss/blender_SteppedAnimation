from bpy.types import Gizmo, GizmoGroup, Context, Operator, IntProperty, Event

class STEPPED_GT_marker_shape(Gizmo):
    def setup(self):
        self.custom_shape = self.new_custom_shape("LINES", (
            (0, 0), (0.5, 1), 
            (0.5, 1), (1, 0),
            (1, 0), (0, 0)
            ))
    
    def draw(self, context:Context):
        self.draw_custom_shape(self.custom_shape)

class STEPPED_GGT_marker(GizmoGroup):
    bl_label = "Stepped marker"
    bl_options = {"PERSISTENT", "SHOW_MODAL_ALL", "SCALE"}
    bl_space_type = "VIEW_3D" #TODO Changer en GRAPH_EDITOR et non DOPESHEET_EDITOR # 'VIEW_3D'
    #'EMPTY', 'VIEW_3D', 'IMAGE_EDITOR', 'NODE_EDITOR', 'SEQUENCE_EDITOR', 'CLIP_EDITOR', 'DOPESHEET_EDITOR', 'GRAPH_EDITOR', 'NLA_EDITOR', 'TEXT_EDITOR', 'CONSOLE', 'INFO', 'TOPBAR', 'STATUSBAR', 'OUTLINER', 'PROPERTIES', 'FILE_BROWSER', 'SPREADSHEET', 'PREFERENCES'
    bl_region_type = "WINDOW" #'WINDOW', 'HEADER', 'CHANNELS', 'TEMPORARY', 'UI', 'TOOLS', 'TOOL_PROPS', 'ASSET_SHELF', 'ASSET_SHELF_HEADER', 'PREVIEW', 'HUD', 'NAVIGATION_BAR', 'EXECUTE', 'FOOTER', 'TOOL_HEADER', 'XR'
    

    def setup(self, context:Context):
        self.udpate_markers(context)
    
    def udpate_markers(self, context:Context):
        nb_markers = len(context.scene.timeline_markers)
        nb_gizmo = len(self.gizmos)
        if nb_gizmo > nb_markers:
            self.remove_markers(nb_gizmo - nb_markers)
        elif nb_gizmo < nb_markers:
            self.add_markers(nb_markers - nb_gizmo)

    def add_markers(self, quantity:int):
        for _ in range(quantity):
            gizmo_marker = self.gizmos.new(STEPPED_GT_marker_shape.__name__)
            gizmo_marker.color = 1.0, 0.0, 0.0
            gizmo_marker.alpha = 0.8
            gizmo_marker.use_draw_modal = True
            gizmo_marker.use_draw_scale = False
    
    def remove_markers(self, quantity:int):
        for i in range(quantity):
            self.gizmos.remove(self.gizmos[i])

    def draw_prepare(self, context: Context):
        tst = context.scene.frame_current*10
        self.udpate_markers(context)
        # w = 110 * context.preferences.system.ui_scale
        # h = 90 * context.preferences.system.ui_scale
        for i in range(len(self.gizmos)):
            # x = context.region.view2d.view_to_region(
            #         x=context.scene.timeline_markers[i].frame, 
            #         y=0, #TODO ne fonctionne qu'avec <=0 pk?
            #         clip=True
            #     )[0]
            self.gizmos[i].matrix_basis[0][3] = tst# + x - 0.5 * w #((vxX, vyX, vzX, vwX) # x pos ?
            self.gizmos[i].matrix_basis[0][0] = tst# + w           # (vxY, vyY, vzY, vwY) # x scale ?
            self.gizmos[i].matrix_basis[1][3] = tst# + 20           # (vxZ, vyZ, vzZ, vwZ) # y pos ?
            self.gizmos[i].matrix_basis[1][1] = tst# + h           # (vxW, vyW, vzW, vwW) # y scale ?