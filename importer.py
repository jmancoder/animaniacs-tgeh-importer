import bpy
from bpy.types import Context, Object
import numpy as np

from . import bmsh_reader


def _import_mesh(context: Context, mesh_data: bmsh_reader.Mesh) -> Object | None:
    if mesh_data.positions is None:
        return None

    if mesh_data.triangles is not None:
        triangles = mesh_data.triangles
    else:
        triangles = []

    # Import and validate geometry
    mesh = bpy.data.meshes.new("Mesh")
    mesh.from_pydata(mesh_data.positions, [], triangles)
    mesh.validate()
    mesh.update()

    # Import vertex normals
    if mesh_data.normals is not None:
        mesh.normals_split_custom_set_from_vertices(mesh_data.normals)

    # Import vertex UVs
    for uvs in (mesh_data.uvs_0, mesh_data.uvs_1):
        if uvs is None:
            continue
        uv_layer = mesh.uv_layers.new()
        vertex_idx_array = np.empty(len(mesh.loops), dtype=np.int32)
        mesh.loops.foreach_get("vertex_index", vertex_idx_array)
        uv_layer.uv.foreach_set("vector", uvs[vertex_idx_array].ravel())

    # Import vertex colors
    if mesh_data.colors is not None:
        vertex_color_attr = mesh.color_attributes.new(
            name="vertex_color",
            type="FLOAT_COLOR",
            domain="POINT",
        )
        vertex_color_attr.data.foreach_set(
            "color",
            mesh_data.colors,
        )

    # Create mesh object
    mesh_obj = bpy.data.objects.new("Mesh", mesh)
    context.collection.objects.link(mesh_obj)
    return mesh_obj


def import_bmsh(context: Context, bmsh_data: bmsh_reader.BMSHData) -> None:
    for mesh_data in bmsh_data.meshes:
        _import_mesh(context, mesh_data)
