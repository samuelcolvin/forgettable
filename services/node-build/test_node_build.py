"""Tests for the node-build server."""

import os

import pytest
import requests

BASE_URL = os.getenv('BASE_URL', 'http://localhost:3003')
BUILD_URL = f'{BASE_URL}/build'
HEALTH_URL = f'{BASE_URL}/health'


@pytest.fixture
def simple_react_app() -> dict[str, str]:
    return {
        'app.tsx': """
export default function App() {
  return <div>Hello, World!</div>;
}
""",
    }


@pytest.fixture
def react_app_with_tailwind() -> dict[str, str]:
    return {
        'app.tsx': """
import "./styles.css";

export default function App() {
  return (
    <div className="p-4 bg-blue-500 text-white rounded-lg">
      Hello, Tailwind!
    </div>
  );
}
""",
        'styles.css': '@import "tailwindcss";',
    }


# Health endpoint tests


def test_health_returns_ok() -> None:
    response = requests.get(HEALTH_URL)
    assert response.status_code == 200
    assert response.text == 'OK'


# Validation tests


def test_rejects_empty_files() -> None:
    payload: dict[str, dict[str, str]] = {'files': {}}
    response = requests.post(BUILD_URL, json=payload)
    assert response.status_code == 400
    assert 'at least one file' in response.text.lower()


def test_rejects_missing_files() -> None:
    payload: dict[str, str] = {}
    response = requests.post(BUILD_URL, json=payload)
    assert response.status_code == 400


def test_rejects_invalid_json() -> None:
    response = requests.post(BUILD_URL, data='not valid json', headers={'Content-Type': 'application/json'})
    assert response.status_code == 400
    assert 'invalid json' in response.text.lower()


# Build success tests


def test_builds_simple_react_app(simple_react_app: dict[str, str]) -> None:
    payload = {'files': simple_react_app}
    response = requests.post(BUILD_URL, json=payload, timeout=60)
    assert response.status_code == 200

    output = response.json()
    assert 'compiled' in output
    assert 'source' in output
    assert len(output['compiled']) > 0


def test_output_contains_js_file(simple_react_app: dict[str, str]) -> None:
    payload = {'files': simple_react_app}
    response = requests.post(BUILD_URL, json=payload, timeout=60)
    assert response.status_code == 200

    compiled = response.json()['compiled']
    js_files = [k for k in compiled if k.endswith('.js')]
    assert len(js_files) >= 1, 'Expected at least one JS file in output'


def test_output_contains_sourcemap(simple_react_app: dict[str, str]) -> None:
    payload = {'files': simple_react_app}
    response = requests.post(BUILD_URL, json=payload, timeout=60)
    assert response.status_code == 200

    compiled = response.json()['compiled']
    map_files = [k for k in compiled if k.endswith('.js.map')]
    assert len(map_files) >= 1, 'Expected at least one sourcemap file in output'


def test_builds_app_with_tailwind(react_app_with_tailwind: dict[str, str]) -> None:
    payload = {'files': react_app_with_tailwind}
    response = requests.post(BUILD_URL, json=payload, timeout=60)
    assert response.status_code == 200

    compiled = response.json()['compiled']
    css_files = [k for k in compiled if k.endswith('.css')]
    assert len(css_files) >= 1, 'Expected at least one CSS file in output'


def test_tailwind_processes_utilities(react_app_with_tailwind: dict[str, str]) -> None:
    payload = {'files': react_app_with_tailwind}
    response = requests.post(BUILD_URL, json=payload, timeout=60)
    assert response.status_code == 200

    compiled = response.json()['compiled']
    css_files = [k for k in compiled if k.endswith('.css')]
    assert len(css_files) >= 1

    css_content = compiled[css_files[0]]
    assert 'bg-blue-500' in css_content or 'blue' in css_content.lower()


def test_output_files_are_in_assets_directory(simple_react_app: dict[str, str]) -> None:
    payload = {'files': simple_react_app}
    response = requests.post(BUILD_URL, json=payload, timeout=60)
    assert response.status_code == 200

    compiled = response.json()['compiled']
    for key in compiled:
        assert key == 'index.html' or key.startswith('assets/'), f'Expected file {key} to be in assets/'


def test_js_output_contains_react_code(simple_react_app: dict[str, str]) -> None:
    payload = {'files': simple_react_app}
    response = requests.post(BUILD_URL, json=payload, timeout=60)
    assert response.status_code == 200

    compiled = response.json()['compiled']
    js_files = [k for k in compiled if k.endswith('.js') and not k.endswith('.map')]
    assert len(js_files) >= 1

    js_content = compiled[js_files[0]]
    assert len(js_content) > 100, 'JS bundle seems too small'


# Build error tests


def test_returns_error_for_missing_app() -> None:
    payload = {
        'files': {
            'other.tsx': """
export default function Other() {
  return <div>Other</div>;
}
"""
        },
    }
    response = requests.post(BUILD_URL, json=payload, timeout=60)
    assert response.status_code == 400
    assert 'app' in response.text.lower() or 'resolve' in response.text.lower()


def test_returns_error_for_missing_import() -> None:
    payload = {
        'files': {
            'app.tsx': """
import { NonExistent } from "./missing";

export default function App() {
  return <div>{NonExistent}</div>;
}
"""
        },
    }
    response = requests.post(BUILD_URL, json=payload, timeout=60)
    assert response.status_code == 400
    assert 'missing' in response.text.lower() or 'resolve' in response.text.lower()


def test_returns_error_for_syntax_error() -> None:
    payload = {
        'files': {
            'app.tsx': """
export default function App() {
  return <div>
  // missing closing tags
"""
        },
    }
    response = requests.post(BUILD_URL, json=payload, timeout=60)
    assert response.status_code == 400


def test_error_response_is_plain_text() -> None:
    payload = {
        'files': {'app.tsx': 'import "./nonexistent";'},
    }
    response = requests.post(BUILD_URL, json=payload, timeout=60)
    assert response.status_code == 400
    content_type = response.headers.get('content-type', '')
    assert 'text/plain' in content_type or 'application/json' not in content_type


# Multiple files tests


def test_builds_app_with_multiple_components() -> None:
    payload = {
        'files': {
            'app.tsx': """
import Header from "./components/Header";
import Footer from "./components/Footer";

export default function App() {
  return (
    <div>
      <Header />
      <main>Content</main>
      <Footer />
    </div>
  );
}
""",
            'components/Header.tsx': """
export default function Header() {
  return <header>Header</header>;
}
""",
            'components/Footer.tsx': """
export default function Footer() {
  return <footer>Footer</footer>;
}
""",
        },
    }
    response = requests.post(BUILD_URL, json=payload, timeout=60)
    assert response.status_code == 200

    compiled = response.json()['compiled']
    js_files = [k for k in compiled if k.endswith('.js') and not k.endswith('.map')]
    assert len(js_files) >= 1


def test_builds_app_with_nested_directories() -> None:
    payload = {
        'files': {
            'app.tsx': """
import { useCounter } from "./hooks/useCounter";

export default function App() {
  const count = useCounter();
  return <div>Count: {count}</div>;
}
""",
            'hooks/useCounter.ts': """
import { useState } from "react";

export function useCounter() {
  const [count] = useState(0);
  return count;
}
""",
        },
    }
    response = requests.post(BUILD_URL, json=payload, timeout=60)
    assert response.status_code == 200


# TypeScript tests


def test_builds_with_typescript_types() -> None:
    payload = {
        'files': {
            'app.tsx': """
interface AppProps {
  name?: string;
}

export default function App({ name = "World" }: AppProps) {
  return <div>Hello, {name}!</div>;
}
""",
        },
    }
    response = requests.post(BUILD_URL, json=payload, timeout=60)
    assert response.status_code == 200


def test_builds_with_type_only_imports() -> None:
    payload = {
        'files': {
            'app.tsx': """
import type { User } from "./types";

const user: User = { id: 1, name: "Test" };

export default function App() {
  return <div>{user.name}</div>;
}
""",
            'types.ts': """
export interface User {
  id: number;
  name: string;
}
""",
        },
    }
    response = requests.post(BUILD_URL, json=payload, timeout=60)
    assert response.status_code == 200


# shadcn/ui component tests


def test_builds_app_with_shadcn_button() -> None:
    payload = {
        'files': {
            'app.tsx': """
import { Button } from "shadcn/components/ui/button";

export default function App() {
  return (
    <div className="p-4">
      <Button>Click me</Button>
      <Button variant="secondary">Secondary</Button>
      <Button variant="destructive">Delete</Button>
    </div>
  );
}
""",
        },
    }
    response = requests.post(BUILD_URL, json=payload, timeout=60)
    assert response.status_code == 200

    compiled = response.json()['compiled']
    js_files = [k for k in compiled if k.endswith('.js') and not k.endswith('.map')]
    assert len(js_files) >= 1


def test_builds_app_with_shadcn_card() -> None:
    payload = {
        'files': {
            'app.tsx': """
import { Card, CardHeader, CardTitle, CardDescription, CardContent, CardFooter } from "shadcn/components/ui/card";
import { Button } from "shadcn/components/ui/button";

export default function App() {
  return (
    <Card className="w-96">
      <CardHeader>
        <CardTitle>Card Title</CardTitle>
        <CardDescription>Card description goes here</CardDescription>
      </CardHeader>
      <CardContent>
        <p>Card content</p>
      </CardContent>
      <CardFooter>
        <Button>Action</Button>
      </CardFooter>
    </Card>
  );
}
""",
        },
    }
    response = requests.post(BUILD_URL, json=payload, timeout=60)
    assert response.status_code == 200


def test_builds_app_with_shadcn_input_and_label() -> None:
    payload = {
        'files': {
            'app.tsx': """
import { Input } from "shadcn/components/ui/input";
import { Label } from "shadcn/components/ui/label";

export default function App() {
  return (
    <div className="space-y-2">
      <Label htmlFor="email">Email</Label>
      <Input id="email" type="email" placeholder="Enter your email" />
    </div>
  );
}
""",
        },
    }
    response = requests.post(BUILD_URL, json=payload, timeout=60)
    assert response.status_code == 200


def test_builds_app_with_lucide_icons() -> None:
    payload = {
        'files': {
            'app.tsx': """
import { Plus, Settings, User } from "lucide-react";
import { Button } from "shadcn/components/ui/button";

export default function App() {
  return (
    <div className="flex gap-2">
      <Button><Plus /> Add</Button>
      <Button variant="outline"><Settings /></Button>
      <Button variant="ghost"><User /></Button>
    </div>
  );
}
""",
        },
    }
    response = requests.post(BUILD_URL, json=payload, timeout=60)
    assert response.status_code == 200


def test_builds_app_with_multiple_shadcn_components() -> None:
    payload = {
        'files': {
            'app.tsx': """
import { Button } from "shadcn/components/ui/button";
import { Card, CardHeader, CardTitle, CardContent } from "shadcn/components/ui/card";
import { Input } from "shadcn/components/ui/input";
import { Label } from "shadcn/components/ui/label";
import { Badge } from "shadcn/components/ui/badge";
import { Checkbox } from "shadcn/components/ui/checkbox";
import { Separator } from "shadcn/components/ui/separator";

export default function App() {
  return (
    <Card className="w-96">
      <CardHeader>
        <CardTitle>
          Todo App <Badge>New</Badge>
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="flex items-center gap-2">
          <Input placeholder="Add a task" />
          <Button>Add</Button>
        </div>
        <Separator />
        <div className="space-y-2">
          <div className="flex items-center gap-2">
            <Checkbox id="task1" />
            <Label htmlFor="task1">Complete project</Label>
          </div>
          <div className="flex items-center gap-2">
            <Checkbox id="task2" />
            <Label htmlFor="task2">Review code</Label>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
""",
        },
    }
    response = requests.post(BUILD_URL, json=payload, timeout=60)
    assert response.status_code == 200
