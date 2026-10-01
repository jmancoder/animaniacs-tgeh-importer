from io import BufferedReader
import logging
from typing import NamedTuple

import numpy as np
import numpy.typing as npt

from .binary_reader import BinaryReader

logger = logging.getLogger(__name__)


class Mesh(NamedTuple):
    triangles: npt.NDArray | None
    positions: npt.NDArray | None
    normals: npt.NDArray | None
    colors: npt.NDArray | None
    uvs_0: npt.NDArray | None
    uvs_1: npt.NDArray | None


class BMSHData(NamedTuple):
    meshes: list[Mesh]


def _read_mesh_buffers_0(bs: BinaryReader, buffer_sizes: list[int]) -> Mesh:
    # Read header
    bs.read_uint32()
    bs.read_uint32()
    vertex_count = bs.read_uint32()
    bs.seek(28, 1)
    skin_related_0 = bs.read_uint32()
    skin_related_1 = bs.read_uint32()
    tri_idx_count = bs.read_uint32()
    bs.seek(20, 1)

    # Read triangles
    buffer_size = buffer_sizes[1]
    if buffer_size > 0:
        triangles = np.frombuffer(
            bs.getbuffer(), "<u2", tri_idx_count, bs.tell()
        ).reshape(-1, 3)
        bs.seek(buffer_size, 1)
    else:
        triangles = None

    # Read positions
    buffer_size = buffer_sizes[2]
    if buffer_size > 0:
        positions = np.frombuffer(
            bs.getbuffer(), "<f4", vertex_count * 3, bs.tell()
        ).reshape(-1, 3)
        bs.seek(buffer_size, 1)
    else:
        positions = None

    # Read normals
    buffer_size = buffer_sizes[3]
    if buffer_size > 0:
        normals = np.frombuffer(
            bs.getbuffer(),
            "<f4",
            vertex_count * 3,
            bs.tell(),
        ).reshape(-1, 3)
        bs.seek(buffer_size, 1)
    else:
        normals = None

    # Read colors
    buffer_size = buffer_sizes[4]
    if buffer_size > 0:
        colors = np.frombuffer(bs.getbuffer(), "<f4", vertex_count * 4, bs.tell())
        bs.seek(buffer_size, 1)
    else:
        colors = None

    # Read UVs
    buffer_size = buffer_sizes[5]
    if buffer_size > 0:
        uvs_0 = np.frombuffer(
            bs.getbuffer(),
            "<f4",
            vertex_count * 2,
            bs.tell(),
        ).reshape(-1, 2)
        bs.seek(buffer_size, 1)
    else:
        uvs_0 = None

    # Read alternate UVs
    buffer_size = buffer_sizes[6]
    if buffer_size > 0:
        uvs_1 = np.frombuffer(
            bs.getbuffer(),
            "<f4",
            vertex_count * 2,
            bs.tell(),
        ).reshape(-1, 2)
        bs.seek(buffer_size, 1)
    else:
        uvs_1 = None

    # Skip over remaining buffers
    if len(buffer_sizes) > 7:
        for buffer_size in buffer_sizes[7:]:
            bs.seek(buffer_size, 1)
    return Mesh(triangles, positions, normals, colors, uvs_0, uvs_1)


def _read_mesh_buffers_1(bs: BinaryReader, buffer_sizes: list[int]) -> Mesh:
    # Read header
    bs.read_uint32()
    vertex_count = bs.read_uint32()
    bs.read_uint32()
    bs.read_float()

    # Read positions
    buffer_size = buffer_sizes[2]
    if buffer_size > 0:
        positions = np.frombuffer(
            bs.getbuffer(), "<f4", vertex_count * 3, bs.tell()
        ).reshape(-1, 3)
        bs.seek(buffer_size, 1)
    else:
        positions = None

    # Skip over remaining buffers
    if len(buffer_sizes) > 10:
        for buffer_size in buffer_sizes[10:]:
            bs.seek(buffer_size, 1)
    return Mesh(None, positions, None, None, None, None)


def _read_mesh(bs: BinaryReader) -> Mesh:
    logger.debug("Reading mesh at 0x%X", bs.tell())

    # Read header
    buffer_count = bs.read_uint32()
    total_buffer_size = bs.read_uint32()
    buffer_sizes = [bs.read_uint32() for _ in range(buffer_count)]
    mesh_end = bs.tell() + total_buffer_size

    # Read buffers
    mesh_type = bs.read_uint32()
    if mesh_type == 0:
        mesh = _read_mesh_buffers_0(bs, buffer_sizes)
    elif mesh_type == 1:
        mesh = _read_mesh_buffers_1(bs, buffer_sizes)
    else:
        logger.warning("Skipped mesh of unimplemented type %d", mesh_type)
        mesh = Mesh(None, None, None, None, None, None)
    bs.seek(mesh_end)
    return mesh


def read_bmsh(f: BufferedReader) -> BMSHData:
    bs = BinaryReader(f.read())

    # Read header
    bs.read_uint32()
    file_type = bs.read_uint32()
    bs.read_uint32()

    # Skip material data for now
    buffer_count = bs.read_uint32()
    total_buffer_size = bs.read_uint32()
    buffer_sizes = [bs.read_int32() for _ in range(buffer_count)]
    bs.seek(total_buffer_size, 1)

    # Read meshes
    meshes = []
    while bs.tell() < bs.getbuffer().nbytes:
        mesh = _read_mesh(bs)
        if mesh is not None:
            meshes.append(mesh)
    else:
        logger.debug("Reached end of file")
    logger.info("Read %d mesh(es)", len(meshes))
    return BMSHData(meshes)
