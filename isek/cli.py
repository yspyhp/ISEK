#!/usr/bin/env python
import click
import importlib.util
import subprocess
import sys
from pathlib import Path


def load_module(script_path: Path):
    """Dynamically load module"""
    try:
        module_name = script_path.stem
        spec = importlib.util.spec_from_file_location(module_name, script_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module
    except Exception as e:
        click.secho(f"Module load error: {e}", fg="red")
        sys.exit(1)


def get_available_examples(ctx, args, incomplete):
    """Get available example scripts"""
    examples_dir = Path(__file__).parent.parent / "examples"
    return [
        f.stem
        for f in examples_dir.glob("*.py")
        if f.name != "__init__.py"
        and not f.name.startswith("_")
        and f.stem.startswith(incomplete)
    ]


@click.group()
def cli():
    """ISEK Distributed Multi-Agent Framework CLI"""


@cli.command()
def clean():
    """Run system cleanup script"""
    script_path = Path(__file__).parent.parent / "scripts" / "clean.py"
    module = load_module(script_path)
    module.main()
    click.secho("✓ Cleanup completed", fg="green")


@cli.command()
def registry():
    """Start local development registry"""
    from isek.isek_center import main

    main()


@cli.command()
def setup():
    """Install ISEK Python dependencies and Node.js dependencies"""
    project_root = Path(__file__).parent.parent
    p2p_dir = project_root / "isek" / "protocol" / "p2p"

    # Install Python dependencies
    try:
        subprocess.check_call(
            [sys.executable, "-m", "pip", "install", "-e", str(project_root)]
        )
        click.secho("✓ Python dependencies installed", fg="green")
    except subprocess.CalledProcessError as e:
        click.secho(f"Python dependency installation failed: {e}", fg="red")
        sys.exit(e.returncode)

    # Install Node.js dependencies
    if p2p_dir.exists() and (p2p_dir / "package.json").exists():
        try:
            subprocess.check_call(["npm", "install"], cwd=str(p2p_dir))
            click.secho("✓ Node.js dependencies installed", fg="green")
        except subprocess.CalledProcessError as e:
            click.secho(f"Node.js dependency installation failed: {e}", fg="red")
            sys.exit(e.returncode)
    else:
        click.secho(
            "⚠ No package.json found in p2p directory, skipping npm install",
            fg="yellow",
        )


@cli.group()
def example():
    """Example script management"""


@example.command()
def list():
    """List available example scripts"""
    examples_dir = Path(__file__).parent.parent / "examples"
    examples = [
        f.stem
        for f in examples_dir.glob("*.py")
        if f.name != "__init__.py" and not f.name.startswith("_")
    ]

    click.echo("Available examples:")
    for name in sorted(examples):
        click.echo(f"  • {name}")


@example.command(
    context_settings=dict(ignore_unknown_options=True, allow_extra_args=True)
)
@click.argument("name", type=click.STRING, shell_complete=get_available_examples)
@click.pass_context
def run(ctx, name: str):
    """Execute specific example script"""
    script_path = Path(__file__).parent.parent / "examples" / f"{name}.py"

    module = load_module(script_path)
    if hasattr(module, "main"):
        extra_args = ctx.args
        module.main(*extra_args) if extra_args else module.main()
        click.secho(f"✓ Example '{name}' completed", fg="green")
    else:
        click.secho(f"✗ Example '{name}' lacks main() function", fg="red")
        sys.exit(1)


if __name__ == "__main__":
    cli()
