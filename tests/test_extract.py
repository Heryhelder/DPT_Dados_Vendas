from pathlib import Path

import pandas as pd
import pytest

from src.extract import extract_csv

DATA_DIR = Path(__file__).parent / "data"


def test_basic_csv_loading():
    df = extract_csv(str(DATA_DIR / "sample_10rows.csv"))
    assert isinstance(df, pd.DataFrame)
    assert len(df) == 10
    assert list(df.columns) == ["id", "nome", "valor", "data", "ativo"]


def test_type_inference():
    df = extract_csv(str(DATA_DIR / "sample_10rows.csv"))
    assert pd.api.types.is_integer_dtype(df["id"])
    assert pd.api.types.is_float_dtype(df["valor"])
    assert pd.api.types.is_datetime64_any_dtype(df["data"])
    assert pd.api.types.is_integer_dtype(df["ativo"])
    assert pd.api.types.is_object_dtype(df["nome"])


def test_structured_logging(caplog):
    caplog.set_level("INFO")
    extract_csv(str(DATA_DIR / "sample_10rows.csv"))
    assert len(caplog.records) >= 1
    log_msg = caplog.records[0].getMessage()
    assert "sample_10rows.csv" in log_msg
    assert "10" in log_msg


def test_custom_delimiter():
    df = extract_csv(str(DATA_DIR / "sample_semicolon.csv"), delimiter=";")
    assert len(df) == 3
    assert list(df.columns) == ["id", "nome", "valor"]


def test_custom_encoding():
    df = extract_csv(str(DATA_DIR / "sample_latin1.csv"), encoding="latin-1")
    assert len(df) == 3
    assert df.loc[0, "nome"] == "João"
    assert df.loc[0, "cidade"] == "São Paulo"


def test_file_not_found():
    with pytest.raises(FileNotFoundError, match="Arquivo não encontrado"):
        extract_csv(str(DATA_DIR / "nao_existe.csv"))


def test_empty_csv():
    with pytest.raises(ValueError, match="CSV vazio"):
        extract_csv(str(DATA_DIR / "sample_empty.csv"))


def test_malformed_csv():
    with pytest.raises(ValueError, match="CSV malformado"):
        extract_csv(str(DATA_DIR / "sample_malformed.csv"))


def test_file_size_exceeded(monkeypatch):
    monkeypatch.setattr("src.config.MAX_FILE_SIZE", 1)
    with pytest.raises(ValueError, match="excede o limite de 100MB"):
        extract_csv(str(DATA_DIR / "sample_10rows.csv"))


def test_explicit_dtypes():
    df = extract_csv(
        str(DATA_DIR / "sample_dtypes.csv"),
        dtypes={"id": str, "data_str": str},
    )
    assert pd.api.types.is_object_dtype(df["id"])
    assert pd.api.types.is_object_dtype(df["data_str"])
    assert df["id"].iloc[0] == "1"
