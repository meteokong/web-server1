"""Unit tests for the CodeFile SQLAlchemy model.

Column/constraint expectations are asserted against data-model.md's
`code_files` table and T009's migration
(backend/alembic/versions/001_initial_schema.py).
"""

from src.models.code_file import CodeFile


def test_tablename_is_code_files():
    assert CodeFile.__tablename__ == "code_files"


def test_has_expected_columns():
    columns = CodeFile.__table__.columns
    expected = {
        "id",
        "uploaded_code_id",
        "file_name",
        "file_path",
        "file_extension",
        "file_size_bytes",
        "storage_path",
        "mime_type",
        "created_at",
    }
    assert expected.issubset(set(columns.keys()))


def test_id_is_primary_key():
    assert CodeFile.__table__.columns["id"].primary_key is True


def test_uploaded_code_id_is_foreign_key_to_uploaded_code_not_nullable():
    col = CodeFile.__table__.columns["uploaded_code_id"]
    assert col.nullable is False
    fk_targets = {fk.target_fullname for fk in col.foreign_keys}
    assert "uploaded_code.id" in fk_targets


def test_file_name_is_not_nullable():
    assert CodeFile.__table__.columns["file_name"].nullable is False


def test_storage_path_is_not_nullable():
    assert CodeFile.__table__.columns["storage_path"].nullable is False


def test_instantiation_sets_given_fields():
    import uuid

    uploaded_code_id = uuid.uuid4()
    code_file = CodeFile(
        uploaded_code_id=uploaded_code_id,
        file_name="main.py",
        file_path="src/main.py",
        file_extension=".py",
        file_size_bytes=2048,
        storage_path="storage/uploads/u1/t1/main.py",
        mime_type="text/x-python",
    )
    assert code_file.uploaded_code_id == uploaded_code_id
    assert code_file.file_name == "main.py"
    assert code_file.file_path == "src/main.py"
    assert code_file.file_extension == ".py"
    assert code_file.file_size_bytes == 2048
    assert code_file.storage_path == "storage/uploads/u1/t1/main.py"
    assert code_file.mime_type == "text/x-python"
