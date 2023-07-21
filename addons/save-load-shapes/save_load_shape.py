import bpy


class SAVE_LOAD_SHAPES_OT_SaveShape(bpy.types.Operator):
    bl_idname = "save_load_shapes.save_shape"
    bl_label = "Save Shape"
    bl_description = "Save Shape"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        obj = bpy.context.active_object

        bpy.ops.object.mode_set(mode="OBJECT")

        clone_obj = obj.copy()
        clone_obj.name = obj.name + "_saved"
        clone_obj.data = obj.data.copy()
        clone_obj.data.name = obj.data.name + "_saved"

        for item in obj.save_load_shapes.saved_shapes:
            if item.name == obj.save_load_shapes.save_name:
                item.obj = clone_obj
                bpy.ops.object.mode_set(mode="EDIT")
                return {"FINISHED"}

        data = obj.save_load_shapes.saved_shapes.add()
        data.name = obj.save_load_shapes.save_name
        data.obj = clone_obj

        bpy.ops.object.mode_set(mode="EDIT")

        return {"FINISHED"}


class SAVE_LOAD_SHAPES_OT_LoadShape(bpy.types.Operator):
    bl_idname = "save_load_shapes.load_shape"
    bl_label = "Load Shape"
    bl_description = "Load Shape"
    bl_options = {"REGISTER", "UNDO"}

    index: bpy.props.IntProperty(options={"HIDDEN"})

    def execute(self, context):
        obj = bpy.context.active_object

        bpy.ops.object.mode_set(mode="OBJECT")

        clone_obj = obj.save_load_shapes.saved_shapes[self.index].obj

        if clone_obj is None:
            raise Exception(f"No saved mesh {self.item_name} in {obj.name}")

        if obj.type == "MESH":
            for v in obj.data.vertices:
                if v.select:
                    v.co = clone_obj.data.vertices[v.index].co

            for group in obj.vertex_groups:
                clone_group = clone_obj.vertex_groups.get(group.name)
                if clone_group is None:
                    continue
                for i in range(len(obj.data.vertices)):
                    try:
                        value = clone_group.weight(i)
                        group.add([i], value, "REPLACE")
                    except RuntimeError:
                        group.remove([i])

        if obj.type == "CURVE":
            for spline_index, spline in enumerate(obj.data.splines):
                for bp_index, bp in enumerate(spline.bezier_points):
                    copy_bp = clone_obj.data.splines[spline_index].bezier_points[
                        bp_index
                    ]
                    bp.co = copy_bp.co
                    bp.handle_left = copy_bp.handle_left
                    bp.handle_right = copy_bp.handle_right
                for p_index, p in enumerate(spline.points):
                    copy_p = clone_obj.data.splines[spline_index].points[p_index]
                    p.co = copy_p.co

        bpy.ops.object.mode_set(mode="EDIT")

        return {"FINISHED"}


class SAVE_LOAD_SHAPES_OT_DeleteShape(bpy.types.Operator):
    bl_idname = "save_load_shapes.delete_shape"
    bl_label = "Delete Shape"
    bl_description = "Delete Shape"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        obj = bpy.context.active_object

        i = 0
        while i < len(obj.save_load_shapes.saved_shapes):
            if (
                obj.save_load_shapes.saved_shapes[i].name
                == obj.save_load_shapes.delete_name
            ):
                obj.save_load_shapes.saved_shapes.remove(i)
            else:
                i += 1

        return {"FINISHED"}


class SAVE_LOAD_SHAPES_UL_LoadListItem(bpy.types.UIList):
    def draw_item(
        self, context, layout, data, item, icon, active_data, active_propname, index
    ):
        obj = bpy.context.active_object
        if obj is None:
            return
        if self.layout_type in {"DEFAULT", "COMPACT"}:
            layout.label(text=item.name)
            layout.operator(
                SAVE_LOAD_SHAPES_OT_LoadShape.bl_idname,
                text="Load",
            ).index = index


class SAVE_LOAD_SHAPES_PT_Panel(bpy.types.Panel):
    bl_label = "Save Load Shapes"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Save Load Shapes"
    bl_context = "mesh_edit"

    def draw_header(self, context):
        layout = self.layout
        layout.label(text="", icon="MESH_DATA")

    def draw(self, context):
        layout = self.layout

        obj = bpy.context.active_object
        if obj is None:
            return

        box = layout.box()
        row = box.row()
        row.label(text="Save")
        row.prop(obj.save_load_shapes, "save_name", text="")
        row.operator(SAVE_LOAD_SHAPES_OT_SaveShape.bl_idname)

        box = layout.box()
        box.label(text="Load")
        box.template_list(
            "SAVE_LOAD_SHAPES_UL_LoadListItem",
            "load_list",
            obj.save_load_shapes,
            "saved_shapes",
            obj.save_load_shapes,
            "saved_shapes_index",
        )

        box = layout.box()
        row = box.row()
        row.label(text="Delete")
        row.prop(obj.save_load_shapes, "delete_name", text="")
        row.operator(SAVE_LOAD_SHAPES_OT_DeleteShape.bl_idname)


class SAVE_LOAD_SHAPES_PG_SavedShapeItem(bpy.types.PropertyGroup):
    name: bpy.props.StringProperty(default="default")
    obj: bpy.props.PointerProperty(type=bpy.types.Object)


class SAVE_LOAD_SHAPES_PG_Properties(bpy.types.PropertyGroup):
    save_name: bpy.props.StringProperty(default="default")
    delete_name: bpy.props.StringProperty(default="")
    saved_shapes: bpy.props.CollectionProperty(type=SAVE_LOAD_SHAPES_PG_SavedShapeItem)
    saved_shapes_index: bpy.props.IntProperty()


def register():
    bpy.types.Object.save_load_shapes = bpy.props.PointerProperty(
        type=SAVE_LOAD_SHAPES_PG_Properties
    )


def unregister():
    del bpy.types.Object.save_load_shapes
