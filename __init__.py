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

from pathlib import Path

import bpy
from bpy_extras.io_utils import ImportHelper
from bpy.props import StringProperty
from bpy.types import Operator, Context

from . import bmsh_reader, importer


class IMPORT_OT_SCENE_bmsh(Operator, ImportHelper):
    """Load a BMSH file."""

    bl_idname = "import_scene.animaniacs_bmsh"
    bl_label = "Import BMSH"
    filename_ext = ".bmsh"

    filter_glob: StringProperty(
        default="*.bmsh",
        options={"HIDDEN"},
        maxlen=255,
    )

    def execute(self, context: Context):
        in_path = Path(self.filepath)
        with open(in_path, "rb") as f:
            bmsh_data = bmsh_reader.read_bmsh(f)

        importer.import_bmsh(context, bmsh_data)
        return {"FINISHED"}


def menu_func_import(self, context):
    self.layout.operator(IMPORT_OT_SCENE_bmsh.bl_idname, text="Animaniacs BMSH (.bmsh)")


def register():
    bpy.utils.register_class(IMPORT_OT_SCENE_bmsh)
    bpy.types.TOPBAR_MT_file_import.append(menu_func_import)


def unregister():
    bpy.utils.unregister_class(IMPORT_OT_SCENE_bmsh)
    bpy.types.TOPBAR_MT_file_import.remove(menu_func_import)


if __name__ == "__main__":
    register()
