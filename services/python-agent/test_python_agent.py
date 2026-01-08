"""Tests for the React builder agent API."""

import requests

BASE_URL = 'http://localhost:3003'


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
    files = {
        'src/App.tsx': """\
import { useState } from 'react';

/**
 * Main App component with a simple counter.
 */
export default function App() {
    const [count, setCount] = useState(0);

    return (
        <div className="p-4">
            <h1 className="text-2xl font-bold">Counter: {count}</h1>
            <button
                className="bg-blue-500 text-white px-4 py-2 rounded"
                onClick={() => setCount(count + 1)}
            >
                Increment
            </button>
        </div>
    );
}
""",
    }

    response = requests.post(
        f'{BASE_URL}/apps/edit',
        json={
            'prompt': 'Add a decrement button next to the increment button',
            'files': files,
        },
        timeout=120,
    )
    assert response.status_code == 200
    data = response.json()
    assert 'diffs' in data
    assert 'files' in data
    assert 'summary' in data
    assert 'src/App.tsx' in data['files']
