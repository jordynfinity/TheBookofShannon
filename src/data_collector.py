import asyncio
import aiohttp
import aiofiles
from bs4 import BeautifulSoup
from pathlib import Path
import csv
import json
from datetime import datetime
import logging
from typing import Dict, List, Any, Optional
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
import multiprocessing
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TimeElapsedColumn
from rich.console import Console
from rich.table import Table
import pandas as pd
import numpy as np
from config_manager import ConfigManager

class DataCollector:
    def __init__(self, config: ConfigManager):
        self.config = config
        self.console = Console()
        self.data_dir = Path("data")
        self.data_dir.mkdir(exist_ok=True)
        self.max_workers = max(1, multiprocessing.cpu_count() // 2)  # Use half of available cores
        self.session = None
        
    async def initialize(self):
        """Initialize the data collector with faith"""
        self.session = aiohttp.ClientSession()
        
    async def close(self):
        """Close the data collector with faith"""
        if self.session:
            await self.session.close()
            
    async def crawl_website(self, url: str, max_pages: int = 10) -> List[Dict[str, Any]]:
        """Crawl a website with faith and collect data"""
        visited = set()
        to_visit = {url}
        data = []
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TimeElapsedColumn(),
            console=self.console
        ) as progress:
            task = progress.add_task(f"[cyan]Crawling {url}...", total=max_pages)
            
            while to_visit and len(visited) < max_pages:
                current_url = to_visit.pop()
                if current_url in visited:
                    continue
                    
                try:
                    async with self.session.get(current_url) as response:
                        if response.status == 200:
                            html = await response.text()
                            soup = BeautifulSoup(html, 'html.parser')
                            
                            # Extract data
                            page_data = {
                                'url': current_url,
                                'title': soup.title.string if soup.title else '',
                                'text': soup.get_text(),
                                'links': [a.get('href') for a in soup.find_all('a', href=True)],
                                'timestamp': datetime.now().isoformat()
                            }
                            data.append(page_data)
                            
                            # Add new links to visit
                            for link in page_data['links']:
                                if link.startswith('http') and link not in visited:
                                    to_visit.add(link)
                                    
                except Exception as e:
                    logging.error(f"Error crawling {current_url}: {e}")
                    
                visited.add(current_url)
                progress.update(task, advance=1)
                
        return data
        
    async def save_data(self, data: List[Dict[str, Any]], format: str = 'json'):
        """Save collected data with faith"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        if format == 'json':
            file_path = self.data_dir / f'crawl_data_{timestamp}.json'
            async with aiofiles.open(file_path, 'w') as f:
                await f.write(json.dumps(data, indent=2))
                
        elif format == 'csv':
            file_path = self.data_dir / f'crawl_data_{timestamp}.csv'
            if data:
                df = pd.DataFrame(data)
                df.to_csv(file_path, index=False)
                
        elif format == 'md':
            file_path = self.data_dir / f'crawl_data_{timestamp}.md'
            async with aiofiles.open(file_path, 'w') as f:
                await f.write(f"# Web Crawl Data - {timestamp}\n\n")
                for item in data:
                    await f.write(f"## {item['title']}\n")
                    await f.write(f"URL: {item['url']}\n")
                    await f.write(f"Timestamp: {item['timestamp']}\n\n")
                    await f.write(f"Content:\n{item['text'][:500]}...\n\n")
                    
        return file_path
        
    async def process_data(self, data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Process collected data with faith using multiple threads"""
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # Process text data
            text_data = list(executor.map(self._process_text, [item['text'] for item in data]))
            
            # Process links
            link_data = list(executor.map(self._process_links, [item['links'] for item in data]))
            
            # Calculate statistics
            stats = {
                'total_pages': len(data),
                'total_links': sum(len(links) for links in link_data),
                'avg_text_length': np.mean([len(text) for text in text_data]),
                'unique_domains': len(set(url.split('/')[2] for item in data for url in item['links']))
            }
            
            return stats
            
    def _process_text(self, text: str) -> str:
        """Process text data with faith"""
        # Remove extra whitespace and normalize
        return ' '.join(text.split())
        
    def _process_links(self, links: List[str]) -> List[str]:
        """Process links with faith"""
        # Normalize and filter links
        return [link for link in links if link.startswith('http')]
        
    async def analyze_data(self, data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze collected data with faith using multiple processes"""
        with ProcessPoolExecutor(max_workers=self.max_workers) as executor:
            # Analyze text content
            text_analysis = list(executor.map(self._analyze_text, [item['text'] for item in data]))
            
            # Analyze link patterns
            link_analysis = list(executor.map(self._analyze_links, [item['links'] for item in data]))
            
            # Combine results
            analysis = {
                'text_stats': {
                    'avg_length': np.mean([stats['length'] for stats in text_analysis]),
                    'avg_word_count': np.mean([stats['word_count'] for stats in text_analysis]),
                    'avg_sentence_count': np.mean([stats['sentence_count'] for stats in text_analysis])
                },
                'link_stats': {
                    'avg_links_per_page': np.mean([stats['link_count'] for stats in link_analysis]),
                    'unique_domains': len(set(domain for stats in link_analysis for domain in stats['domains']))
                }
            }
            
            return analysis
            
    def _analyze_text(self, text: str) -> Dict[str, Any]:
        """Analyze text with faith"""
        words = text.split()
        sentences = text.split('.')
        return {
            'length': len(text),
            'word_count': len(words),
            'sentence_count': len(sentences)
        }
        
    def _analyze_links(self, links: List[str]) -> Dict[str, Any]:
        """Analyze links with faith"""
        domains = set(url.split('/')[2] for url in links if url.startswith('http'))
        return {
            'link_count': len(links),
            'domains': list(domains)
        }
        
    def display_results(self, stats: Dict[str, Any], analysis: Dict[str, Any]):
        """Display results with faith using rich"""
        # Create stats table
        stats_table = Table(title="Crawl Statistics")
        stats_table.add_column("Metric", style="cyan")
        stats_table.add_column("Value", style="green")
        
        for key, value in stats.items():
            stats_table.add_row(key.replace('_', ' ').title(), str(value))
            
        # Create analysis table
        analysis_table = Table(title="Data Analysis")
        analysis_table.add_column("Category", style="cyan")
        analysis_table.add_column("Metric", style="yellow")
        analysis_table.add_column("Value", style="green")
        
        for category, metrics in analysis.items():
            for metric, value in metrics.items():
                analysis_table.add_row(
                    category.replace('_', ' ').title(),
                    metric.replace('_', ' ').title(),
                    f"{value:.2f}"
                )
                
        # Display tables
        self.console.print(stats_table)
        self.console.print(analysis_table)
        
async def main():
    config = ConfigManager()
    collector = DataCollector(config)
    await collector.initialize()
    
    try:
        # Crawl example website
        data = await collector.crawl_website("https://example.com", max_pages=5)
        
        # Save data in multiple formats
        json_file = await collector.save_data(data, 'json')
        csv_file = await collector.save_data(data, 'csv')
        md_file = await collector.save_data(data, 'md')
        
        # Process and analyze data
        stats = await collector.process_data(data)
        analysis = await collector.analyze_data(data)
        
        # Display results
        collector.display_results(stats, analysis)
        
    finally:
        await collector.close()

if __name__ == "__main__":
    asyncio.run(main()) 