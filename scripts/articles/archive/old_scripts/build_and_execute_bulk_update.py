#!/usr/bin/env python3
"""
Build and execute the bulk outline update.
This script loads outlines, fetches articles (via MCP), matches them, and generates SQL.
"""

import json
import logging
from bulk_update_outlines import build_bulk_update_sql

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Load extracted outlines
logger.info("Loading extracted outlines...")
with open('scripts/articles/extracted_outlines.json', 'r', encoding='utf-8') as f:
    outlines_by_title = json.load(f)

logger.info(f"Loaded {len(outlines_by_title)} outlines")

# Articles will be fetched via MCP Supabase
# Query: SELECT slug, title, category FROM general_articles WHERE status = 'draft_outline' ORDER BY slug

logger.info("\n" + "="*60)
logger.info("Ready to build bulk update SQL")
logger.info("="*60)
logger.info("\nThe assistant will now:")
logger.info("1. Fetch articles from database")
logger.info("2. Match with outlines")
logger.info("3. Generate and execute SQL")
logger.info("="*60)

