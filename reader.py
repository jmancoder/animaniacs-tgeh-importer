import logging
from pathlib import Path

from .binary_reader import BinaryReader
from . import bmsh_reader, bskl_reader

logger = logging.getLogger(__name__)


def read_file(
    input_path: Path, read_col_meshes: bool
) -> tuple[int, bmsh_reader.Model | bskl_reader.Skeleton | None]:
    with open(input_path, "rb") as f:
        bs = BinaryReader(f.read())

    if bs.getbuffer().nbytes < 12:
        logger.error("File %s too small to parse", input_path.name)
        return -1, None

    # Read shared header
    asset_id = bs.read_uint32()
    bs.read_uint32()
    bs.read_uint32()

    if input_path.suffix == ".bmsh":
        return asset_id, bmsh_reader.read_bmsh(bs, read_col_meshes)
    elif input_path.suffix == ".bskl":
        return asset_id, bskl_reader.read_bskl(bs)
    else:
        logger.error("Unrecognized file extension %s", input_path.suffix)
        return asset_id, None
