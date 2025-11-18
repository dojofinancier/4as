#!/usr/bin/env python3
"""
Execute all outline updates automatically
This script will run all SQL files from seq_updates/ directory one by one
"""

import os
import sys
from pathlib import Path
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('outline_updates_execution.log', encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

def main():
    """Execute all SQL files from seq_updates directory"""
    seq_updates_dir = Path('scripts/articles/seq_updates')
    
    if not seq_updates_dir.exists():
        logger.error(f"Directory not found: {seq_updates_dir}")
        sys.exit(1)
    
    # Get all SQL files sorted by name
    sql_files = sorted(seq_updates_dir.glob('do_batch_*.sql'))
    
    logger.info(f"Found {len(sql_files)} SQL files to execute")
    
    # Read each SQL file and print it for the assistant to execute via MCP
    for i, sql_file in enumerate(sql_files, 1):
        logger.info(f"Processing {i}/{len(sql_files)}: {sql_file.name}")
        
        try:
            sql_content = sql_file.read_text(encoding='utf-8')
            
            # Output the SQL content so the assistant can execute it via MCP
            print(f"\n{'='*60}")
            print(f"FILE: {sql_file.name}")
            print(f"{'='*60}")
            print(sql_content)
            print(f"{'='*60}\n")
            
        except Exception as e:
            logger.error(f"Error reading {sql_file.name}: {e}")
    
    logger.info(f"Finished processing {len(sql_files)} files")
    logger.info("Assistant will now execute these via MCP Supabase")

if __name__ == '__main__':
    main()

