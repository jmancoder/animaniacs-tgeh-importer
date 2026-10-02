bl_info = {
    "name": "ADDON_NAME",
    "author": "AUTHOR_NAME",
    "description": "",
    "blender": (2, 80, 0),
    "version": (0, 0, 1),
    "location": "File > Import",
    "warning": "",
    "category": "Import-Export",
}

import logging
from pathlib import Path

import bpy
from bpy_extras.io_utils import ImportHelper
from bpy.props import CollectionProperty, FloatProperty, StringProperty
from bpy.types import Context, Object, Operator, OperatorFileListElement

from . import bmsh_reader, bskl_reader, reader, importer

# Set up logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler()
handler.setFormatter(logging.Formatter("%(levelname)s: %(message)s"))
logger.addHandler(handler)


class IMPORT_OT_SCENE_bmsh_bskl(Operator, ImportHelper):
    """Load a BMSH and/or BSKL file."""

    bl_idname = "import_scene.bmsh_bskl"
    bl_label = "Import BMSH/BSKL"
    filename_ext = ".bmsh;.bskl"

    filter_glob: StringProperty(
        default="*.bmsh;*.bskl",
        options={"HIDDEN"},
        maxlen=255,
    )

    directory: StringProperty(
        subtype="DIR_PATH",
        options={"SKIP_SAVE", "HIDDEN"},
    )

    files: CollectionProperty(
        type=OperatorFileListElement,
        options={"SKIP_SAVE", "HIDDEN"},
    )

    bone_length: FloatProperty(
        name="Bone Length",
        description="The length of each bone. Adjust according to the model size.",
        default=5.0,
        subtype="DISTANCE",
    )

    def execute(self, context: Context):
        # Read files and group them by asset ID
        asset_map = {}
        for in_path_str in self.files:
            input_path = Path(self.directory) / in_path_str.name
            asset_id, asset_data = reader.read_file(input_path)
            if asset_id > -1 and asset_data is not None:
                if asset_id in asset_map:
                    asset_map[asset_id].append(asset_data)
                else:
                    asset_map[asset_id] = [asset_data]

        for data_list in asset_map.values():
            # Import first skeleton
            armature_obj = None
            bone_names = []
            for data in data_list:
                if type(data) is bskl_reader.Skeleton:
                    armature_obj = importer.import_armature(
                        context, data, self.bone_length
                    )
                    bone_names = [bone.name for bone in data.bones]
                    break

            # Import models
            for data in data_list:
                if type(data) is bmsh_reader.Model:
                    importer.import_model(context, data, armature_obj, bone_names)
        return {"FINISHED"}


def menu_func_import(self, context):
    self.layout.operator(
        IMPORT_OT_SCENE_bmsh_bskl.bl_idname, text="Animaniacs BMSH/BSKL (.bmsh/.bskl)"
    )


def register():
    bpy.utils.register_class(IMPORT_OT_SCENE_bmsh_bskl)
    bpy.types.TOPBAR_MT_file_import.append(menu_func_import)


def unregister():
    bpy.utils.unregister_class(IMPORT_OT_SCENE_bmsh_bskl)
    bpy.types.TOPBAR_MT_file_import.remove(menu_func_import)


if __name__ == "__main__":
    register()
