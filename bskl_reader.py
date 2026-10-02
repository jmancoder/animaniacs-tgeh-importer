import logging
from typing import NamedTuple

from mathutils import Matrix

from .binary_reader import BinaryReader

logger = logging.getLogger(__name__)


class Bone(NamedTuple):
    name: str
    parent_id: int
    rest_transform: Matrix
    inverse_transform: Matrix
    unk_transform: Matrix


class Skeleton(NamedTuple):
    bone_ids: list[int]
    bones: list[Bone]


def read_skeleton_0(bs: BinaryReader, buffer_sizes: list[int]) -> Skeleton:
    # Read header
    header_end = bs.tell() + buffer_sizes[0] - 4
    bone_count = bs.read_uint32()
    bs.read_uint32()
    bone_ids = [bs.read_int8() for _ in range(bone_count)]
    bs.seek(header_end)

    # Read bones
    bones: list[Bone] = []
    for _ in range(bone_count):
        name = bs.read_string_block(44)
        parent_id = bs.read_int32()
        matrix_0 = bs.read_matrix_4x4()
        matrix_1 = bs.read_matrix_4x4()
        matrix_2 = bs.read_matrix_4x4()
        bones.append(Bone(name, parent_id, matrix_0, matrix_1, matrix_2))
    return Skeleton(bone_ids, bones)


def read_bskl(bs: BinaryReader) -> Skeleton:
    # Read file header
    buffer_count = bs.read_uint32()
    total_buffer_size = bs.read_uint32()
    buffer_sizes = [bs.read_uint32() for _ in range(buffer_count)]
    skeleton_end = bs.tell() + total_buffer_size

    # Read skeleton header
    skeleton_type = bs.read_uint32()
    if skeleton_type == 0:
        skeleton = read_skeleton_0(bs, buffer_sizes)
    else:
        logger.error("Skipping skeleton of unimplemented type %d", skeleton_type)
        skeleton = Skeleton([], [])

    bs.seek(skeleton_end)
    return skeleton
