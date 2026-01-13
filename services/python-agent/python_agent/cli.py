"""CLI for the React builder agent."""

import argparse
import asyncio
import sys
from pathlib import Path

import httpx

from .agent import BUILD_ENDPOINT, run_agent

HELLO_WORLD_APP = """\
/**
 * A simple Hello World React component.
 */
export default function App(): JSX.Element {
  return (
    <div className="flex items-center justify-center min-h-screen bg-gray-100">
      <h1 className="text-4xl font-bold text-blue-600">Hello World</h1>
    </div>
  );
}
"""


async def test_build_connection() -> dict[str, str]:
    """Test the connection to the build service with a hello world app.

    Returns:
        The compiled files from the build service.

    Raises:
        RuntimeError: If the build service returns an error.
    """
    async with httpx.AsyncClient() as client:
        response = await client.post(
            BUILD_ENDPOINT,
            json={'files': {'app.tsx': HELLO_WORLD_APP}},
            timeout=60.0,
        )
        if response.status_code != 200:
            raise RuntimeError(f'Build failed ({response.status_code}): {response.text}')
        return response.json()


def read_source_files(app_dir: Path) -> dict[str, str]:
    """Read existing TypeScript/TSX files from app directory.

    Args:
        app_dir: Path to the app directory (reads from src/ subdirectory).

    Returns:
        Dict mapping file paths to their contents.
    """
    files: dict[str, str] = {}
    src_dir = app_dir / 'src'

    if not src_dir.exists():
        print(f'Error: {src_dir} does not exist', file=sys.stderr)
        sys.exit(1)

    for ext in ('*.ts', '*.tsx'):
        for file_path in src_dir.rglob(ext):
            rel_path = file_path.relative_to(src_dir)
            files[str(rel_path)] = file_path.read_text()

    return files


def write_output_files(
    outdir: Path,
    source_files: dict[str, str],
    compiled_files: dict[str, str],
) -> None:
    """Write source and compiled files to output directory.

    Args:
        outdir: Base output directory.
        source_files: Dict of source file paths to contents (written to src/).
        compiled_files: Dict of compiled file paths to contents (written to dist/).
    """
    for file_path, content in source_files.items():
        out_path = outdir / 'src' / file_path
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(content)
        print(f'Wrote {out_path}')

    dist_dir = outdir / 'dist'
    for file_path, content in compiled_files.items():
        out_path = dist_dir / file_path
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(content)
        print(f'Wrote {out_path}')


async def cmd_create(outdir: Path, prompt: str) -> None:
    """Create a new React app.

    Args:
        outdir: Directory to write output files to.
        prompt: User prompt describing the app to create.
    """
    print(f'Creating app in {outdir}...')
    print(f'Prompt: {prompt}\n')

    files, compiled_files, summary = await run_agent(prompt)

    outdir.mkdir(parents=True, exist_ok=True)
    write_output_files(outdir, files, compiled_files)

    print(f'\n{summary}')


async def cmd_edit(app_dir: Path, prompt: str) -> None:
    """Edit an existing React app.

    Args:
        app_dir: Directory containing the existing app.
        prompt: User prompt describing the changes to make.
    """
    print(f'Editing app in {app_dir}...')
    print(f'Prompt: {prompt}\n')

    existing_files = read_source_files(app_dir)
    print(f'Read {len(existing_files)} existing files')

    files, compiled_files, summary = await run_agent(prompt, existing_files)

    write_output_files(app_dir, files, compiled_files)

    print(f'\n{summary}')


async def cmd_test() -> None:
    """Test the connection to the node-build service."""
    print('Testing connection to node-build service...')
    print('Submitting hello world app...\n')

    try:
        compiled_files = await test_build_connection()
        print('Success! Received compiled files:')
        for file_path in compiled_files:
            print(f'  - {file_path}')
    except Exception as e:
        print(f'Error: {e}', file=sys.stderr)
        sys.exit(1)


def main() -> None:
    """CLI entry point."""
    parser = argparse.ArgumentParser(
        description='React builder agent CLI',
        prog='uv run python-agent',
    )
    subparsers = parser.add_subparsers(dest='command', required=True)

    create_parser = subparsers.add_parser('create', help='Create a new React app')
    create_parser.add_argument('outdir', type=Path, help='Output directory for the app')
    create_parser.add_argument('prompt', help='Description of the app to create')

    edit_parser = subparsers.add_parser('edit', help='Edit an existing React app')
    edit_parser.add_argument('app_dir', type=Path, help='Directory containing the existing app')
    edit_parser.add_argument('prompt', help='Description of the changes to make')

    subparsers.add_parser('test', help='Test connection to node-build service')

    args = parser.parse_args()

    if args.command == 'create':
        asyncio.run(cmd_create(args.outdir, args.prompt))
    elif args.command == 'edit':
        asyncio.run(cmd_edit(args.app_dir, args.prompt))
    elif args.command == 'test':
        asyncio.run(cmd_test())


if __name__ == '__main__':
    main()
