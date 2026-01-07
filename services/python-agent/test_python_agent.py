"""Tests for the React builder agent API."""

import pytest
import requests

BASE_URL = 'http://localhost:8000'


def test_create_app() -> None:
    """Test creating a new React app."""
    response = requests.post(
        f'{BASE_URL}/apps',
        json={'prompt': 'Create a simple counter app with increment and decrement buttons'},
        timeout=120,
    )
    assert response.status_code == 200
    data = response.json()
    assert 'files' in data
    assert 'summary' in data
    assert len(data['files']) > 0


def test_edit_app() -> None:
    """Test editing an existing app."""
    # First create an app
    create_resp = requests.post(
        f'{BASE_URL}/apps',
        json={'prompt': 'Create a simple counter app'},
        timeout=120,
    )
    assert create_resp.status_code == 200
    files = create_resp.json()['files']

    # Then edit it
    edit_resp = requests.post(
        f'{BASE_URL}/apps/edit',
        json={
            'prompt': 'Add a reset button to the counter that sets the count back to zero',
            'files': files,
        },
        timeout=120,
    )
    assert edit_resp.status_code == 200
    data = edit_resp.json()
    assert 'diffs' in data
    assert 'files' in data
    assert 'summary' in data


def test_create_app_includes_typescript() -> None:
    """Verify generated files are TypeScript."""
    response = requests.post(
        f'{BASE_URL}/apps',
        json={'prompt': 'Create a simple todo list app'},
        timeout=120,
    )
    assert response.status_code == 200
    data = response.json()
    # Check all files are .ts or .tsx
    for path in data['files']:
        assert path.endswith('.ts') or path.endswith('.tsx'), f'Non-TS file: {path}'


def test_create_app_has_summary() -> None:
    """Verify the response includes a meaningful summary."""
    response = requests.post(
        f'{BASE_URL}/apps',
        json={'prompt': 'Create a greeting component that says Hello World'},
        timeout=120,
    )
    assert response.status_code == 200
    data = response.json()
    assert 'summary' in data
    assert len(data['summary']) > 0


if __name__ == '__main__':
    pytest.main()
