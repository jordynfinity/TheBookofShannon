from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.prompt import Prompt, Confirm
from rich.markdown import Markdown
from rich.syntax import Syntax
from rich.layout import Layout
from rich.live import Live
from rich import box
import typer
from typing import Optional
import asyncio
from datetime import datetime
import json
from pathlib import Path
import sys
from license_verifier import LicenseVerifier
from config_manager import ConfigManager
from second_zot import SecondZot

app = typer.Typer(help="The Book of Shannon - AI Graph Builder CLI")
console = Console()

def verify_license():
    """Verify license and exit if invalid"""
    is_valid, error = LicenseVerifier.verify_license()
    if not is_valid:
        console.print(Panel(f"[red]License verification failed: {error}[/red]", 
                          title="License Error", 
                          border_style="red"))
        sys.exit(1)
    console.print(Panel("[green]License verified successfully![/green]", 
                       title="License Status", 
                       border_style="green"))

@app.command()
def init():
    """Initialize the application"""
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        transient=True,
    ) as progress:
        progress.add_task("Verifying license...", total=None)
        verify_license()
        
    console.print(Panel(
        "[bold blue]The Book of Shannon[/bold blue]\n"
        "[italic]AI Graph Builder CLI[/italic]",
        title="Welcome",
        border_style="blue"
    ))

@app.command()
def license():
    """Show license information"""
    verify_license()
    license_info = LicenseVerifier.get_license_info()
    
    table = Table(title="License Information", box=box.ROUNDED)
    table.add_column("Property", style="cyan")
    table.add_column("Value", style="green")
    
    for key, value in license_info.items():
        table.add_row(key.replace("_", " ").title(), str(value))
        
    console.print(table)
    
    report = LicenseVerifier.generate_license_report()
    console.print(Panel(Markdown(report), title="License Report"))

@app.command()
def verify(revenue: float = typer.Option(0.0, help="Total revenue"),
          profit: float = typer.Option(0.0, help="Total profit")):
    """Verify derivative work compliance"""
    verify_license()
    is_compliant, message = LicenseVerifier.verify_derivative_work(revenue, profit)
    
    if is_compliant:
        console.print(Panel(message, title="Compliance Check", border_style="green"))
    else:
        console.print(Panel(message, title="Compliance Check", border_style="red"))

@app.command()
def graph():
    """Interactive graph visualization"""
    verify_license()
    
    # Create layout
    layout = Layout()
    layout.split_column(
        Layout(name="header"),
        Layout(name="body"),
        Layout(name="footer")
    )
    
    # Header
    layout["header"].update(Panel(
        "[bold blue]The Book of Shannon[/bold blue] - Graph Visualization",
        border_style="blue"
    ))
    
    # Body
    table = Table(box=box.ROUNDED)
    table.add_column("Node", style="cyan")
    table.add_column("Type", style="green")
    table.add_column("Faith", style="yellow")
    
    # Add sample data
    table.add_row("First Zot", "zot", "100%")
    table.add_row("Second Zot", "zot", "100%")
    
    layout["body"].update(table)
    
    # Footer
    layout["footer"].update(Panel(
        "[italic]Use arrow keys to navigate, 'q' to quit[/italic]",
        border_style="blue"
    ))
    
    with Live(layout, refresh_per_second=4):
        console.print("\nPress 'q' to quit...")
        while True:
            key = console.input()
            if key.lower() == 'q':
                break

@app.command()
def improve():
    """Run improvement process"""
    verify_license()
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        transient=True,
    ) as progress:
        task = progress.add_task("Running improvement...", total=None)
        
        # Simulate improvement process
        asyncio.run(async_improve())
        
    console.print(Panel(
        "[green]Improvement completed successfully![/green]",
        title="Improvement Status",
        border_style="green"
    ))

async def async_improve():
    """Run improvement process asynchronously"""
    config = ConfigManager()
    second_zot = await SecondZot.create(config)
    improvements = await second_zot.find_improvements("")
    
    if improvements:
        console.print(Panel(
            f"Found {len(improvements)} improvements",
            title="Improvement Results",
            border_style="green"
        ))

@app.command()
def config():
    """Show current configuration"""
    verify_license()
    config = ConfigManager()
    
    table = Table(title="Configuration", box=box.ROUNDED)
    table.add_column("Setting", style="cyan")
    table.add_column("Value", style="green")
    
    for key, value in config.get_config().items():
        if isinstance(value, dict):
            for subkey, subvalue in value.items():
                table.add_row(f"{key}.{subkey}", str(subvalue))
        else:
            table.add_row(key, str(value))
            
    console.print(table)

if __name__ == "__main__":
    app() 