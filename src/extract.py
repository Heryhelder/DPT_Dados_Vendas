import logging
import time
from os import PathLike
from pathlib import Path

import pandas as pd

from src import config

logger = logging.getLogger(__name__)


def _count_columns(path: Path, delimiter: str, encoding: str) -> int:
    with path.open(encoding=encoding) as f:
        header = f.readline()
    return len(header.rstrip("\n").split(delimiter))


def _validate_columns(path: Path, delimiter: str, encoding: str) -> None:
    expected = _count_columns(path, delimiter, encoding)
    with path.open(encoding=encoding) as f:
        f.readline()
        for line_no, line in enumerate(f, start=2):
            stripped = line.rstrip("\n")
            if not stripped:
                continue
            actual = len(stripped.split(delimiter))
            if actual != expected:
                raise ValueError(
                    f"CSV malformado em {path}: "
                    f"linha {line_no} tem {actual} colunas, "
                    f"esperava {expected}"
                )


def extract_csv(
    file_path: str | PathLike,
    delimiter: str = config.DEFAULT_DELIMITER,
    encoding: str = config.DEFAULT_ENCODING,
    dtypes: dict[str, type] | None = None,
) -> pd.DataFrame:
    path = Path(file_path)

    if not path.exists():
        raise FileNotFoundError(f"Arquivo não encontrado: {path}")

    file_size = path.stat().st_size
    if file_size > config.MAX_FILE_SIZE:
        raise ValueError(
            f"Arquivo excede o limite de 100MB: {path} "
            f"({file_size / 1024 / 1024:.1f}MB)"
        )

    if file_size == 0:
        raise ValueError(f"CSV vazio: {path}")

    _start = time.perf_counter()

    raw_encoding = "utf-8-sig" if encoding == "utf-8" else encoding
    # BOM stripping is automatic for UTF-8 via utf-8-sig.
    # Non-UTF-8 encodings with BOM are not handled — callers should
    # strip the BOM upstream for non-UTF-8 files.

    _validate_columns(path, delimiter, raw_encoding)

    df = pd.read_csv(
        path,
        sep=delimiter,
        encoding=raw_encoding,
        dtype=dtypes,
        parse_dates=True,
        skipinitialspace=True,
    )

    if df.empty:
        raise ValueError(f"CSV vazio: {path}")

    for col in df.columns:
        if pd.api.types.is_object_dtype(df[col]) and dtypes is None:
            df[col] = df[col].str.strip()
            try:
                parsed = pd.to_datetime(df[col], format="mixed", errors="raise")
                df[col] = parsed
            except (ValueError, TypeError):
                pass

    elapsed = time.perf_counter() - _start
    logger.info(
        "Extração concluída | path=%s linhas=%d colunas=%d duração=%.2fs",
        str(path),
        len(df),
        len(df.columns),
        elapsed,
    )

    return df
