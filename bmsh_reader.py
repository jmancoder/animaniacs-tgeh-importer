from io import BufferedReader
import logging
from typing import NamedTuple

import numpy as np
import numpy.typing as npt

from .binary_reader import BinaryReader

logger = logging.getLogger(__name__)


class Mesh(NamedTuple):
    positions: npt.NDArray | None
    normals: npt.NDArray | None
    colors: npt.NDArray | None
    uvs_0: npt.NDArray | None
    uvs_1: npt.NDArray | None
    skin_entries: npt.NDArray | None
    triangles: npt.NDArray | None


class BMSHData(NamedTuple):
    meshes: list[Mesh]


def _read_mesh_11(bs: BinaryReader) -> Mesh:
    # Read mesh header
    geom_size = bs.read_uint32()
    geom_header_size = bs.read_uint32()
    tri_buf_size = bs.read_uint32()
    pos_buf_size = bs.read_uint32()
    norm_buf_size = bs.read_uint32()
    color_buf_size = bs.read_uint32()
    uv_0_buf_size = bs.read_uint32()
    uv_1_buf_size = bs.read_uint32()
    unk_buf_size_0 = bs.read_uint32()
    unk_buf_size_1 = bs.read_uint32()
    skin_buf_size = bs.read_uint32()
    unk_buf_size_2 = bs.read_uint32()

    # Read geometry header
    bs.read_uint32()
    bs.read_uint32()
    bs.read_uint32()
    vertex_count = bs.read_uint32()
    bs.seek(36, 1)
    tri_idx_count = bs.read_uint32()
    bs.seek(20, 1)

    # Read geometry buffers
    if tri_buf_size > 0:
        prim_indices = np.frombuffer(
            bs.getbuffer(), "<u2", tri_idx_count, bs.tell()
        ).reshape(-1, 3)
        bs.seek(tri_buf_size, 1)
    else:
        prim_indices = None

    if pos_buf_size > 0:
        positions = np.frombuffer(
            bs.getbuffer(), "<f4", vertex_count * 3, bs.tell()
        ).reshape(-1, 3)
        bs.seek(pos_buf_size, 1)
    else:
        positions = None

    if norm_buf_size > 0:
        normals = np.frombuffer(
            bs.getbuffer(),
            "<f4",
            vertex_count * 3,
            bs.tell(),
        ).reshape(-1, 3)
        bs.seek(norm_buf_size, 1)
    else:
        normals = None

    if color_buf_size > 0:
        colors = np.frombuffer(bs.getbuffer(), "<f4", vertex_count * 4, bs.tell())
        bs.seek(color_buf_size, 1)
    else:
        colors = None

    if uv_0_buf_size > 0:
        uvs_0 = np.frombuffer(
            bs.getbuffer(),
            "<f4",
            vertex_count * 2,
            bs.tell(),
        ).reshape(-1, 2)
        bs.seek(uv_0_buf_size, 1)
    else:
        uvs_0 = None

    if uv_1_buf_size > 0:
        uvs_1 = np.frombuffer(
            bs.getbuffer(),
            "<f4",
            vertex_count * 2,
            bs.tell(),
        ).reshape(-1, 2)
        bs.seek(uv_1_buf_size, 1)
    else:
        uvs_1 = None

    bs.seek(unk_buf_size_0, 1)
    bs.seek(unk_buf_size_1, 1)

    if skin_buf_size > 0:
        skin_entries = np.frombuffer(
            bs.getbuffer(),
            "<f4",
            vertex_count * 24,
            bs.tell(),
        ).reshape(-1, 24)
        bs.seek(skin_buf_size, 1)
    else:
        skin_entries = None

    bs.seek(unk_buf_size_2, 1)
    return Mesh(positions, normals, colors, uvs_0, uvs_1, skin_entries, prim_indices)


def _read_mesh_18(bs: BinaryReader) -> Mesh:
    geom_size = bs.read_uint32()
    bs.read_uint32()
    bs.read_uint32()
    bs.read_uint32()
    bs.read_uint32()
    bs.read_uint32()
    bs.read_uint32()
    bs.read_uint32()
    bs.read_uint32()
    bs.read_uint32()
    bs.read_uint32()
    bs.read_uint32()
    bs.read_uint32()
    bs.read_uint32()
    bs.read_uint32()
    bs.read_uint32()
    bs.read_uint32()
    bs.read_uint32()
    bs.read_uint32()

    bs.seek(geom_size, 1)
    return Mesh(None, None, None, None, None, None, None)


def read_bmsh(f: BufferedReader) -> BMSHData:
    bs = BinaryReader(f.read())

    # Read file header
    bs.read_uint32()
    bs.read_uint32()
    bs.read_uint32()
    header_type = bs.read_uint32()
    material_chunk_size = bs.read_uint32()
    bs.read_uint32()
    bs.read_uint32()
    bs.read_uint32()
    bs.read_uint32()
    bs.read_uint32()
    bs.read_uint32()
    bs.read_uint32()
    if header_type == 7:
        pass
    elif header_type == 12:
        bs.seek(20, 1)
    elif header_type == 17:
        bs.seek(40, 1)
    else:
        logger.warning("Unimplemented header type ID %d", header_type)

    # Skip texture and material data for now
    bs.seek(material_chunk_size, 1)

    # Read meshes
    meshes = []
    while bs.tell() < bs.getbuffer().nbytes:
        mesh_type = bs.read_uint32()
        if mesh_type == 11:
            logger.debug("Reading mesh type 11 at 0x%X", bs.tell())
            meshes.append(_read_mesh_11(bs))
        elif mesh_type == 18:
            logger.debug("Skipping mesh type 18 at 0x%X", bs.tell())
            _read_mesh_18(bs)
        else:
            logger.warning("Unimplemented mesh type ID %d", mesh_type)
            break
    logger.info("Successfully read %d mesh(es)", len(meshes))
    return BMSHData(meshes)
