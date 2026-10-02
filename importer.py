import bpy
from bpy.types import Context, Object
import numpy as np

from . import bmsh_reader, bskl_reader


def import_armature(
    context: Context, skeleton: bskl_reader.Skeleton, bone_length: float
) -> Object:
    armature = bpy.data.armatures.new("Armature")
    armature_obj = bpy.data.objects.new("Armature", armature)
    context.collection.objects.link(armature_obj)

    context.view_layer.objects.active = armature_obj
    bpy.ops.object.mode_set(mode="EDIT")
    for bone_data in skeleton.bones:
        bone = armature.edit_bones.new(bone_data.name)
        bone.length = bone_length
        if bone_data.parent_id > -1:
            bone.parent = armature.edit_bones[bone_data.parent_id]
        bone.matrix = bone_data.rest_transform

    bpy.ops.object.mode_set(mode="OBJECT")
    return armature_obj


def _import_mesh(
    context: Context, mesh_data: bmsh_reader.Mesh, bone_names: list[str]
) -> Object | None:
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

    # Create and import vertex groups
    if mesh_data.weights is not None:
        vertex_groups = [
            mesh_obj.vertex_groups.new(name=bone_name) for bone_name in bone_names
        ]
        for i, weight_array in enumerate(mesh_data.weights):
            for vertex_group, weight in zip(vertex_groups, weight_array):
                if weight > 0.0:
                    vertex_group.add([i], weight, "ADD")
    return mesh_obj


def import_model(
    context: Context,
    model_data: bmsh_reader.Model,
    armature_object: Object | None,
    bone_names: list[str],
) -> None:
    for mesh_data in model_data.meshes:
        mesh_obj = _import_mesh(context, mesh_data, bone_names)

        # Attach to armature if present
        if mesh_obj is None or armature_object is None:
            continue
        mesh_obj.parent = armature_object
        modifier = mesh_obj.modifiers.new("Armature", "ARMATURE")
        modifier.object = armature_object
