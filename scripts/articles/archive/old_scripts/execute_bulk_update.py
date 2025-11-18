#!/usr/bin/env python3
"""
Execute the bulk outline update by:
1. Reading extracted outlines
2. Fetching articles from database (via MCP - this script prepares the query)
3. Building and saving the SQL
"""

import json
import logging
from bulk_update_outlines import read_all_outline_sql_files, build_bulk_update_sql

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def main():
    # Step 1: Extract outlines
    logger.info("Extracting outlines from SQL files...")
    outlines_by_title = read_all_outline_sql_files()
    
    if not outlines_by_title:
        logger.error("No outlines found!")
        return
    
    logger.info(f"Extracted {len(outlines_by_title)} outlines")
    
    # Step 2: The articles will be fetched via MCP Supabase
    # For now, save the outlines to a JSON file for the assistant to use
    with open('scripts/articles/extracted_outlines.json', 'w', encoding='utf-8') as f:
        json.dump(outlines_by_title, f, ensure_ascii=False, indent=2)
    
    logger.info("Outlines saved to scripts/articles/extracted_outlines.json")
    logger.info("Assistant will:")
    logger.info("1. Fetch articles from database")
    logger.info("2. Load this JSON file")
    logger.info("3. Match and build SQL")

if __name__ == '__main__':
    main()

