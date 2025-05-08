#!/usr/bin/env python3
"""
Manual File Processor for ETL Extraction Agent

This script manually processes files in the data/raw directory without using watchdog.
It's useful for testing the ETL agent's functionality without having to install the watchdog package.
"""

import os
import sys
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('manual_processor')

# Try to import required modules
try:
    import pandas as pd
except ImportError:
    logger.error("Error: pandas package not found. Please install it using 'pip install pandas'")
    sys.exit(1)

# Import the ETL agent modules
try:
    from etl_agent import (
        DataExtractor, 
        DataNormalizer, 
        MetadataManager, 
        DataForwarder,
        RAW_DATA_DIR,
        PROCESSED_DATA_DIR
    )
except ImportError as e:
    logger.error(f"Error importing from etl_agent: {e}")
    logger.error("Make sure you're running this script from the etl_agent directory")
    sys.exit(1)

def process_file(file_path):
    """
    Process a single file using the ETL agent components.
    
    Args:
        file_path: Path to the file to process
    """
    try:
        logger.info(f"Processing file: {file_path}")
        
        # Extract data from the file
        df, source_format = DataExtractor.extract_from_file(file_path)
        
        # Normalize the data
        normalized_df = DataNormalizer.normalize(df)
        
        # Attach metadata
        payload = MetadataManager.attach_metadata(
            normalized_df, 
            os.path.basename(file_path),
            source_format
        )
        
        # Prepare for message passing (future integration)
        prepared_payload = DataForwarder.prepare_for_message_passing(payload)
        
        # Forward to processed directory
        output_path = DataForwarder.forward_to_processed(
            prepared_payload,
            os.path.basename(file_path)
        )
        
        logger.info(f"File processed successfully: {file_path} -> {output_path}")
        return True
        
    except Exception as e:
        logger.error(f"Error processing file {file_path}: {e}")
        return False

def main():
    """Process all CSV and JSON files in the raw data directory."""
    logger.info(f"Looking for files in: {RAW_DATA_DIR}")
    
    # Ensure the raw and processed directories exist
    os.makedirs(RAW_DATA_DIR, exist_ok=True)
    os.makedirs(PROCESSED_DATA_DIR, exist_ok=True)
    
    # Get all CSV and JSON files in the raw directory
    files_to_process = []
    for filename in os.listdir(RAW_DATA_DIR):
        file_path = os.path.join(RAW_DATA_DIR, filename)
        
        # Only process files (not directories)
        if os.path.isfile(file_path):
            file_extension = os.path.splitext(file_path)[1].lower()
            
            # Only process CSV and JSON files
            if file_extension in ['.csv', '.json']:
                files_to_process.append(file_path)
    
    if not files_to_process:
        logger.info(f"No CSV or JSON files found in {RAW_DATA_DIR}")
        return
    
    logger.info(f"Found {len(files_to_process)} files to process")
    
    # Process each file
    success_count = 0
    for file_path in files_to_process:
        if process_file(file_path):
            success_count += 1
    
    logger.info(f"Processing complete. {success_count}/{len(files_to_process)} files processed successfully.")
    
    # Show the processed files
    processed_files = os.listdir(PROCESSED_DATA_DIR)
    if processed_files:
        logger.info(f"Processed files in {PROCESSED_DATA_DIR}:")
        for filename in processed_files:
            logger.info(f"  - {filename}")

if __name__ == "__main__":
    main()
