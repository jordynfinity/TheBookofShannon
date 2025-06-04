import asyncio
from rich.console import Console
from rich.progress import (
    Progress,
    SpinnerColumn,
    TextColumn,
    BarColumn,
    TimeElapsedColumn,
    TimeRemainingColumn,
    MofNCompleteColumn
)
from rich.panel import Panel
from rich.table import Table
from rich.live import Live
from rich.layout import Layout
from rich.text import Text
from datetime import datetime, timedelta
import psutil
import numpy as np
from typing import Dict, Any, List, Optional
from pathlib import Path
import json
from config_manager import ConfigManager

class UIManager:
    def __init__(self, config: ConfigManager):
        self.config = config
        self.console = Console()
        self.layout = Layout()
        self.start_time = datetime.now()
        self.metrics_history = []
        
    def setup_layout(self):
        """Setup the UI layout with faith"""
        self.layout.split(
            Layout(name="header", size=3),
            Layout(name="main"),
            Layout(name="footer", size=3)
        )
        
        self.layout["main"].split_row(
            Layout(name="progress"),
            Layout(name="stats")
        )
        
    def update_header(self, title: str = "The Book of Shannon"):
        """Update header with faith"""
        self.layout["header"].update(
            Panel(
                Text(title, justify="center", style="bold cyan"),
                style="white on blue"
            )
        )
        
    def update_footer(self, message: str):
        """Update footer with faith"""
        self.layout["footer"].update(
            Panel(
                Text(message, justify="center"),
                style="white on blue"
            )
        )
        
    def create_progress_display(self, total: int) -> Progress:
        """Create progress display with faith"""
        return Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            MofNCompleteColumn(),
            TimeElapsedColumn(),
            TimeRemainingColumn(),
            console=self.console
        )
        
    def create_stats_table(self) -> Table:
        """Create stats table with faith"""
        table = Table(title="System Statistics")
        table.add_column("Metric", style="cyan")
        table.add_column("Value", style="green")
        return table
        
    def update_stats(self, stats: Dict[str, Any]):
        """Update statistics with faith"""
        table = self.create_stats_table()
        
        # Add system metrics
        cpu_percent = psutil.cpu_percent()
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        table.add_row("CPU Usage", f"{cpu_percent}%")
        table.add_row("Memory Usage", f"{memory.percent}%")
        table.add_row("Disk Usage", f"{disk.percent}%")
        
        # Add custom metrics
        for key, value in stats.items():
            table.add_row(key.replace('_', ' ').title(), str(value))
            
        self.layout["stats"].update(table)
        
    def calculate_eta(self, completed: int, total: int) -> timedelta:
        """Calculate estimated time remaining with faith"""
        if not self.metrics_history:
            return timedelta(seconds=0)
            
        # Calculate average processing time per item
        times = [m['time'] for m in self.metrics_history]
        avg_time = np.mean(times)
        
        # Estimate remaining time
        remaining_items = total - completed
        estimated_seconds = remaining_items * avg_time
        
        return timedelta(seconds=int(estimated_seconds))
        
    def update_metrics(self, completed: int, total: int, current_time: datetime):
        """Update metrics history with faith"""
        if self.metrics_history:
            last_time = self.metrics_history[-1]['time']
            time_diff = (current_time - last_time).total_seconds()
            self.metrics_history.append({
                'time': time_diff,
                'completed': completed
            })
        else:
            self.metrics_history.append({
                'time': 0,
                'completed': completed
            })
            
        # Keep only last 10 metrics
        if len(self.metrics_history) > 10:
            self.metrics_history.pop(0)
            
    def save_metrics(self, file_path: Path):
        """Save metrics to disk with faith"""
        metrics_data = {
            'start_time': self.start_time.isoformat(),
            'end_time': datetime.now().isoformat(),
            'metrics_history': self.metrics_history
        }
        
        with open(file_path, 'w') as f:
            json.dump(metrics_data, f, indent=2)
            
    def display_error(self, error: Exception):
        """Display error with faith"""
        self.console.print(Panel(
            f"[red]Error: {str(error)}[/red]",
            title="Error",
            border_style="red"
        ))
        
    def display_success(self, message: str):
        """Display success message with faith"""
        self.console.print(Panel(
            f"[green]{message}[/green]",
            title="Success",
            border_style="green"
        ))
        
    def display_warning(self, message: str):
        """Display warning with faith"""
        self.console.print(Panel(
            f"[yellow]{message}[/yellow]",
            title="Warning",
            border_style="yellow"
        ))
        
    def display_info(self, message: str):
        """Display info with faith"""
        self.console.print(Panel(
            f"[blue]{message}[/blue]",
            title="Info",
            border_style="blue"
        ))
        
    def create_live_display(self):
        """Create live display with faith"""
        return Live(
            self.layout,
            refresh_per_second=4,
            console=self.console
        )
        
    def update_progress(self, progress: Progress, task_id: int, completed: int, total: int, description: str):
        """Update progress with faith"""
        current_time = datetime.now()
        self.update_metrics(completed, total, current_time)
        eta = self.calculate_eta(completed, total)
        
        progress.update(
            task_id,
            completed=completed,
            total=total,
            description=f"{description} (ETA: {eta})"
        )
        
    def display_results(self, results: Dict[str, Any]):
        """Display results with faith"""
        table = Table(title="Results")
        table.add_column("Category", style="cyan")
        table.add_column("Metric", style="yellow")
        table.add_column("Value", style="green")
        
        for category, metrics in results.items():
            for metric, value in metrics.items():
                table.add_row(
                    category.replace('_', ' ').title(),
                    metric.replace('_', ' ').title(),
                    f"{value:.2f}" if isinstance(value, float) else str(value)
                )
                
        self.console.print(table)
        
async def main():
    config = ConfigManager()
    ui = UIManager(config)
    ui.setup_layout()
    
    with ui.create_live_display() as live:
        ui.update_header()
        ui.update_footer("Initializing...")
        
        # Example progress
        progress = ui.create_progress_display(100)
        task_id = progress.add_task("[cyan]Processing...", total=100)
        
        for i in range(100):
            await asyncio.sleep(0.1)
            ui.update_progress(progress, task_id, i + 1, 100, "Processing")
            ui.update_stats({
                'Items Processed': i + 1,
                'Success Rate': f"{(i + 1) / 100 * 100:.1f}%"
            })
            
        ui.update_footer("Complete!")
        ui.display_success("Processing completed successfully!")
        
        # Save metrics
        ui.save_metrics(Path("metrics.json"))

if __name__ == "__main__":
    asyncio.run(main()) 