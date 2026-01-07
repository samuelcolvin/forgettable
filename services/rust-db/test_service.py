# /// script
# requires-python = ">=3.13"
# dependencies = [
#     "pytest",
#     "requests",
# ]
# ///
"""
Integration tests for the KV database service.

Run with: pytest test_node_build.py -v
Requires the server to be running on localhost:3001
"""

import uuid

import pytest
import requests

BASE_URL = "http://localhost:3001"


def create_project() -> str:
    """Helper to create a new project and return its UUID."""
    response = requests.post(f"{BASE_URL}/project/new", timeout=10)
    response.raise_for_status()
    return response.json()["id"]


def test_create_project() -> None:
    """Test creating a new project returns a valid UUID."""
    response = requests.post(f"{BASE_URL}/project/new", timeout=10)

    assert response.status_code == 200
    data = response.json()
    assert "id" in data
    # Validate it's a valid UUID
    uuid.UUID(data["id"])


def test_store_and_get_entry() -> None:
    """Test storing and retrieving a key-value entry."""
    project_id = create_project()
    key = "test-key"
    content = b"Hello, World!"

    # Store entry
    store_response = requests.post(
        f"{BASE_URL}/project/{project_id}/{key}",
        data=content,
        headers={"Content-Type": "text/plain"},
        timeout=10,
    )
    assert store_response.status_code == 201

    # Retrieve entry
    get_response = requests.get(
        f"{BASE_URL}/project/{project_id}/get/{key}",
        timeout=10,
    )
    assert get_response.status_code == 200
    assert get_response.content == content
    assert get_response.headers["Content-Type"] == "text/plain"


def test_store_with_mime_type() -> None:
    """Test that Content-Type header is preserved."""
    project_id = create_project()
    key = "image.png"
    content = b"\x89PNG\r\n\x1a\n"  # PNG magic bytes
    mime_type = "image/png"

    # Store with specific mime type
    store_response = requests.post(
        f"{BASE_URL}/project/{project_id}/{key}",
        data=content,
        headers={"Content-Type": mime_type},
        timeout=10,
    )
    assert store_response.status_code == 201

    # Retrieve and verify mime type
    get_response = requests.get(
        f"{BASE_URL}/project/{project_id}/get/{key}",
        timeout=10,
    )
    assert get_response.status_code == 200
    assert get_response.headers["Content-Type"] == mime_type


def test_store_default_mime_type() -> None:
    """Test that missing Content-Type defaults to application/octet-stream."""
    project_id = create_project()
    key = "binary-data"
    content = b"\x00\x01\x02\x03"

    # Store without Content-Type header
    store_response = requests.post(
        f"{BASE_URL}/project/{project_id}/{key}",
        data=content,
        timeout=10,
    )
    assert store_response.status_code == 201

    # Retrieve and verify default mime type
    get_response = requests.get(
        f"{BASE_URL}/project/{project_id}/get/{key}",
        timeout=10,
    )
    assert get_response.status_code == 200
    assert get_response.headers["Content-Type"] == "application/octet-stream"


def test_list_entries_with_prefix() -> None:
    """Test listing entries by prefix."""
    project_id = create_project()

    # Store multiple entries with common prefix
    entries = [
        ("docs/readme.md", "text/markdown"),
        ("docs/api.md", "text/markdown"),
        ("docs/guide/intro.md", "text/markdown"),
        ("images/logo.png", "image/png"),
    ]

    for key, mime_type in entries:
        requests.post(
            f"{BASE_URL}/project/{project_id}/{key}",
            data=b"content",
            headers={"Content-Type": mime_type},
            timeout=10,
        )

    # List entries with prefix "docs/"
    list_response = requests.get(
        f"{BASE_URL}/project/{project_id}/list/docs/",
        timeout=10,
    )
    assert list_response.status_code == 200

    result: list[dict[str, str]] = list_response.json()
    assert len(result) == 3

    keys = [entry["key"] for entry in result]
    assert "docs/readme.md" in keys
    assert "docs/api.md" in keys
    assert "docs/guide/intro.md" in keys
    assert "images/logo.png" not in keys


def test_list_entries_empty_prefix() -> None:
    """Test listing all entries with empty prefix."""
    project_id = create_project()

    # Store entries
    keys = ["file1.txt", "file2.txt", "nested/file3.txt"]
    for key in keys:
        requests.post(
            f"{BASE_URL}/project/{project_id}/{key}",
            data=b"content",
            headers={"Content-Type": "text/plain"},
            timeout=10,
        )

    # List all entries (empty prefix matches all)
    list_response = requests.get(
        f"{BASE_URL}/project/{project_id}/list/",
        timeout=10,
    )
    assert list_response.status_code == 200

    result: list[dict[str, str]] = list_response.json()
    assert len(result) == 3


def test_delete_entry() -> None:
    """Test deleting an entry."""
    project_id = create_project()
    key = "to-delete"

    # Store entry
    requests.post(
        f"{BASE_URL}/project/{project_id}/{key}",
        data=b"temporary",
        headers={"Content-Type": "text/plain"},
        timeout=10,
    )

    # Delete entry
    delete_response = requests.delete(
        f"{BASE_URL}/project/{project_id}/{key}",
        timeout=10,
    )
    assert delete_response.status_code == 204

    # Verify entry is gone
    get_response = requests.get(
        f"{BASE_URL}/project/{project_id}/get/{key}",
        timeout=10,
    )
    assert get_response.status_code == 404


def test_get_nonexistent_key() -> None:
    """Test 404 for nonexistent key."""
    project_id = create_project()

    response = requests.get(
        f"{BASE_URL}/project/{project_id}/get/nonexistent-key",
        timeout=10,
    )

    assert response.status_code == 404
    data = response.json()
    assert "error" in data


def test_delete_nonexistent_key() -> None:
    """Test 404 when deleting nonexistent key."""
    project_id = create_project()

    response = requests.delete(
        f"{BASE_URL}/project/{project_id}/nonexistent-key",
        timeout=10,
    )

    assert response.status_code == 404


def test_store_to_nonexistent_project() -> None:
    """Test 404 when storing to nonexistent project."""
    fake_project_id = str(uuid.uuid4())

    response = requests.post(
        f"{BASE_URL}/project/{fake_project_id}/some-key",
        data=b"content",
        headers={"Content-Type": "text/plain"},
        timeout=10,
    )

    assert response.status_code == 404
    data = response.json()
    assert "error" in data


def test_nested_key_paths() -> None:
    """Test keys with slashes like 'folder/subfolder/file.txt'."""
    project_id = create_project()
    nested_key = "folder/subfolder/deeply/nested/file.txt"
    content = b"Nested content"

    # Store with nested path
    store_response = requests.post(
        f"{BASE_URL}/project/{project_id}/{nested_key}",
        data=content,
        headers={"Content-Type": "text/plain"},
        timeout=10,
    )
    assert store_response.status_code == 201

    # Retrieve with nested path
    get_response = requests.get(
        f"{BASE_URL}/project/{project_id}/get/{nested_key}",
        timeout=10,
    )
    assert get_response.status_code == 200
    assert get_response.content == content


def test_update_existing_entry() -> None:
    """Test that storing to existing key updates the value."""
    project_id = create_project()
    key = "updatable"

    # Store initial value
    requests.post(
        f"{BASE_URL}/project/{project_id}/{key}",
        data=b"initial",
        headers={"Content-Type": "text/plain"},
        timeout=10,
    )

    # Update with new value and mime type
    requests.post(
        f"{BASE_URL}/project/{project_id}/{key}",
        data=b"updated",
        headers={"Content-Type": "application/json"},
        timeout=10,
    )

    # Verify update
    get_response = requests.get(
        f"{BASE_URL}/project/{project_id}/get/{key}",
        timeout=10,
    )
    assert get_response.status_code == 200
    assert get_response.content == b"updated"
    assert get_response.headers["Content-Type"] == "application/json"


def test_special_characters_in_prefix() -> None:
    """Test that special SQL LIKE characters in prefix are escaped."""
    project_id = create_project()

    # Store entries with special characters
    requests.post(
        f"{BASE_URL}/project/{project_id}/test%file.txt",
        data=b"content1",
        headers={"Content-Type": "text/plain"},
        timeout=10,
    )
    requests.post(
        f"{BASE_URL}/project/{project_id}/test_file.txt",
        data=b"content2",
        headers={"Content-Type": "text/plain"},
        timeout=10,
    )
    requests.post(
        f"{BASE_URL}/project/{project_id}/testXfile.txt",
        data=b"content3",
        headers={"Content-Type": "text/plain"},
        timeout=10,
    )

    # List with prefix containing % - should only match literal %
    list_response = requests.get(
        f"{BASE_URL}/project/{project_id}/list/test%25",  # %25 is URL-encoded %
        timeout=10,
    )
    assert list_response.status_code == 200

    result: list[dict[str, str]] = list_response.json()
    # Should only match "test%file.txt", not use % as wildcard
    assert len(result) == 1
    assert result[0]["key"] == "test%file.txt"


def test_binary_content() -> None:
    """Test storing and retrieving binary content."""
    project_id = create_project()
    key = "binary.bin"
    # Include null bytes and other binary data
    content = bytes(range(256))

    store_response = requests.post(
        f"{BASE_URL}/project/{project_id}/{key}",
        data=content,
        headers={"Content-Type": "application/octet-stream"},
        timeout=10,
    )
    assert store_response.status_code == 201

    get_response = requests.get(
        f"{BASE_URL}/project/{project_id}/get/{key}",
        timeout=10,
    )
    assert get_response.status_code == 200
    assert get_response.content == content


def test_large_content() -> None:
    """Test storing and retrieving larger content."""
    project_id = create_project()
    key = "large.bin"
    # 1MB of data
    content = b"x" * (1024 * 1024)

    store_response = requests.post(
        f"{BASE_URL}/project/{project_id}/{key}",
        data=content,
        headers={"Content-Type": "application/octet-stream"},
        timeout=30,
    )
    assert store_response.status_code == 201

    get_response = requests.get(
        f"{BASE_URL}/project/{project_id}/get/{key}",
        timeout=30,
    )
    assert get_response.status_code == 200
    assert len(get_response.content) == len(content)


def test_project_isolation() -> None:
    """Test that entries are isolated between projects."""
    project1 = create_project()
    project2 = create_project()
    key = "shared-key"

    # Store in project1
    requests.post(
        f"{BASE_URL}/project/{project1}/{key}",
        data=b"project1 content",
        headers={"Content-Type": "text/plain"},
        timeout=10,
    )

    # Store different content in project2
    requests.post(
        f"{BASE_URL}/project/{project2}/{key}",
        data=b"project2 content",
        headers={"Content-Type": "text/plain"},
        timeout=10,
    )

    # Verify isolation
    response1 = requests.get(
        f"{BASE_URL}/project/{project1}/get/{key}",
        timeout=10,
    )
    response2 = requests.get(
        f"{BASE_URL}/project/{project2}/get/{key}",
        timeout=10,
    )

    assert response1.content == b"project1 content"
    assert response2.content == b"project2 content"


if __name__ == "__main__":
    pytest.main()
