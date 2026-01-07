"""Integration tests for the go-main service."""

import uuid

import pytest
import requests

BASE_URL = 'http://localhost:3002'


def test_root_redirects_to_uuid() -> None:
    """Test that / redirects to a new UUID."""
    response = requests.get(f'{BASE_URL}/', allow_redirects=False, timeout=10)
    assert response.status_code == 302
    location = response.headers['Location']
    # Verify it's a valid UUID path
    uuid_part = location.strip('/')
    uuid.UUID(uuid_part)  # Will raise if invalid


def test_project_page_returns_html() -> None:
    """Test that /{uuid} returns HTML."""
    project_id = str(uuid.uuid4())
    response = requests.get(f'{BASE_URL}/{project_id}', timeout=10)
    assert response.status_code == 200
    assert 'text/html' in response.headers['Content-Type']
    assert project_id in response.text


def test_invalid_uuid_returns_400() -> None:
    """Test that invalid UUIDs return 400."""
    response = requests.get(f'{BASE_URL}/not-a-uuid', timeout=10)
    assert response.status_code == 400
    data = response.json()
    assert 'error' in data


def test_view_returns_404_for_new_project() -> None:
    """Test that /{uuid}/view returns 404 when no app exists."""
    project_id = str(uuid.uuid4())
    response = requests.get(f'{BASE_URL}/{project_id}/view', timeout=10)
    assert response.status_code == 404


def test_health_check() -> None:
    """Test health check endpoint."""
    response = requests.get(f'{BASE_URL}/health', timeout=10)
    assert response.status_code == 200
    assert response.text == 'OK'


def test_create_without_prompt_returns_400() -> None:
    """Test that creating without a prompt returns 400."""
    project_id = str(uuid.uuid4())
    response = requests.post(
        f'{BASE_URL}/{project_id}/create',
        json={},
        timeout=10,
    )
    assert response.status_code == 400
    data = response.json()
    assert 'error' in data


def test_create_with_invalid_json_returns_400() -> None:
    """Test that creating with invalid JSON returns 400."""
    project_id = str(uuid.uuid4())
    response = requests.post(
        f'{BASE_URL}/{project_id}/create',
        data='not json',
        headers={'Content-Type': 'application/json'},
        timeout=10,
    )
    assert response.status_code == 400


def test_edit_without_existing_app_returns_error() -> None:
    """Test that editing a non-existent app returns an error."""
    project_id = str(uuid.uuid4())
    response = requests.post(
        f'{BASE_URL}/{project_id}/edit',
        json={'prompt': 'Add something'},
        timeout=30,
    )
    assert response.status_code in [400, 404]


def test_edit_without_prompt_returns_400() -> None:
    """Test that editing without a prompt returns 400."""
    project_id = str(uuid.uuid4())
    response = requests.post(
        f'{BASE_URL}/{project_id}/edit',
        json={},
        timeout=10,
    )
    assert response.status_code == 400


def test_create_app() -> None:
    """Test creating a new app.

    This test requires the Python Agent and Rust DB services to be running.
    """
    project_id = str(uuid.uuid4())
    response = requests.post(
        f'{BASE_URL}/{project_id}/create',
        json={'prompt': 'Create a hello world app that displays "Hello, World!" in the center of the page'},
        timeout=120,
    )
    assert response.status_code == 200
    data = response.json()
    assert 'summary' in data
    assert 'files' in data
    assert 'view_url' in data
    assert data['view_url'] == f'/{project_id}/view'


def test_view_returns_html_after_create() -> None:
    """Test that /{uuid}/view returns HTML after app creation.

    This test requires the Python Agent and Rust DB services to be running.
    """
    project_id = str(uuid.uuid4())

    # Create app first
    create_response = requests.post(
        f'{BASE_URL}/{project_id}/create',
        json={'prompt': 'Create a simple app with a heading that says "Test"'},
        timeout=120,
    )
    assert create_response.status_code == 200

    # Now view should work
    response = requests.get(f'{BASE_URL}/{project_id}/view', timeout=10)
    assert response.status_code == 200
    assert 'text/html' in response.headers['Content-Type']


def test_edit_app() -> None:
    """Test editing an existing app.

    This test requires the Python Agent and Rust DB services to be running.
    """
    project_id = str(uuid.uuid4())

    # Create app first
    create_response = requests.post(
        f'{BASE_URL}/{project_id}/create',
        json={'prompt': 'Create a counter app with an increment button'},
        timeout=120,
    )
    assert create_response.status_code == 200

    # Edit the app
    response = requests.post(
        f'{BASE_URL}/{project_id}/edit',
        json={'prompt': 'Add a decrement button next to the increment button'},
        timeout=120,
    )
    assert response.status_code == 200
    data = response.json()
    assert 'summary' in data
    assert 'files' in data
    assert 'view_url' in data


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
