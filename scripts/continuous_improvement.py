#!/usr/bin/env python3
import sys
from pathlib import Path
import logging
import time
from src.code_rewriter import CodeRewriter

def setup_logging():
    """Setup logging configuration"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('continuous_improvement.log'),
            logging.StreamHandler()
        ]
    )
    return logging.getLogger(__name__)

def main():
    """Main function to run continuous code improvement"""
    logger = setup_logging()
    logger.info("Starting continuous code improvement")
    
    rewriter = CodeRewriter()
    iteration = 0
    max_iterations = 100  # Prevent infinite loops
    
    while iteration < max_iterations:
        logger.info(f"Starting improvement iteration {iteration + 1}")
        
        try:
            if rewriter.increase_linkage_density():
                logger.info("Successfully increased code linkage density")
            else:
                logger.info("No further improvements possible")
                break
                
        except Exception as e:
            logger.error(f"Error during improvement: {e}")
            break
            
        iteration += 1
        time.sleep(1)  # Prevent excessive CPU usage
        
    logger.info(f"Completed {iteration} improvement iterations")

if __name__ == '__main__':
    main() 