#!/usr/bin/env python3
"""
Transformation Agent for ETL Pipeline

This module implements a Transformation Agent for an ETL pipeline that:
1. Monitors the /data/processed folder for new normalized CSV or JSON files
2. Loads each dataset, inspects column names and datatypes
3. Applies a BIM-inspired tagging system to each field
4. Applies data transformations based on tags:
   - Standardizes date formats
   - One-hot encodes categorical variables
   - Normalizes numeric ranges (0-1)
5. Saves the transformed dataset into /data/enriched with the same base filename
6. Maintains a transformation log in /logs/transformation_log.csv

The code is designed to be modular with clear separation between:
- File monitoring
- Data loading and inspection
- Tagging system
- Data transformation
- Metadata management
- Logging
"""

import os
import json
import yaml
import csv
import time
import logging
import datetime
import re
import pandas as pd
import numpy as np
from pathlib import Path
from typing import Dict, List, Any, Union, Optional, Tuple
from datetime import datetime

# Check for required packages
try:
    import pandas as pd
    import numpy as np
    import yaml
    from watchdog.observers import Observer
    from watchdog.events import FileSystemEventHandler, FileCreatedEvent
except ImportError as e:
    print(f"Error: Required package not found: {e}")
    print("\nThis script requires the following packages:")
    print("  - pandas: For data manipulation")
    print("  - numpy: For numerical operations")
    print("  - pyyaml: For YAML file parsing")
    print("  - watchdog: For file monitoring")
    print("\nPlease install them using:")
    print("  pip install pandas numpy pyyaml watchdog")
    print("  or")
    print("  pip3 install pandas numpy pyyaml watchdog")
    exit(1)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('transformation_agent')

# Define constants
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROCESSED_DATA_DIR = os.path.join(SCRIPT_DIR, 'data', 'processed')
ENRICHED_DATA_DIR = os.path.join(SCRIPT_DIR, 'data', 'enriched')
LOGS_DIR = os.path.join(SCRIPT_DIR, 'logs')
CONFIG_DIR = os.path.join(SCRIPT_DIR, 'config')
TAGS_CONFIG_PATH = os.path.join(CONFIG_DIR, 'tags.yaml')
TRANSFORMATION_LOG_PATH = os.path.join(LOGS_DIR, 'transformation_log.csv')


class DataLoader:
    """
    Handles loading data from processed files and inspecting their structure.
    """
    
    @staticmethod
    def load_from_file(file_path: str) -> Tuple[pd.DataFrame, Dict[str, Any]]:
        """
        Load data from a processed file.
        
        Args:
            file_path: Path to the file to load
            
        Returns:
            tuple: (DataFrame containing the data, metadata dictionary)
            
        Raises:
            ValueError: If the file format is not supported
        """
        file_extension = os.path.splitext(file_path)[1].lower()
        
        if file_extension == '.json':
            return DataLoader._load_from_json(file_path)
        elif file_extension == '.csv':
            return DataLoader._load_from_csv(file_path)
        else:
            raise ValueError(f"Unsupported file format: {file_extension}")
    
    @staticmethod
    def _load_from_json(file_path: str) -> Tuple[pd.DataFrame, Dict[str, Any]]:
        """
        Load data from a JSON file.
        
        Args:
            file_path: Path to the JSON file
            
        Returns:
            tuple: (DataFrame containing the data, metadata dictionary)
        """
        logger.info(f"Loading data from JSON file: {file_path}")
        try:
            with open(file_path, 'r') as f:
                content = json.load(f)
            
            # Extract data and metadata
            if isinstance(content, dict) and 'data' in content and 'metadata' in content:
                # File follows the expected structure
                metadata = content['metadata']
                data = content['data']
                df = pd.DataFrame(data)
                return df, metadata
            else:
                # Try to handle as a direct data structure
                df = pd.DataFrame(content)
                metadata = {
                    'filename': os.path.basename(file_path),
                    'timestamp': datetime.now().isoformat(),
                    'source_format': 'json',
                    'row_count': len(df),
                    'column_count': len(df.columns),
                    'columns': list(df.columns)
                }
                return df, metadata
                
        except Exception as e:
            logger.error(f"Error loading data from JSON file: {e}")
            raise
    
    @staticmethod
    def _load_from_csv(file_path: str) -> Tuple[pd.DataFrame, Dict[str, Any]]:
        """
        Load data from a CSV file.
        
        Args:
            file_path: Path to the CSV file
            
        Returns:
            tuple: (DataFrame containing the data, metadata dictionary)
        """
        logger.info(f"Loading data from CSV file: {file_path}")
        try:
            # Read CSV file into a pandas DataFrame
            df = pd.read_csv(file_path)
            
            # Create metadata
            metadata = {
                'filename': os.path.basename(file_path),
                'timestamp': datetime.now().isoformat(),
                'source_format': 'csv',
                'row_count': len(df),
                'column_count': len(df.columns),
                'columns': list(df.columns)
            }
            
            return df, metadata
        except Exception as e:
            logger.error(f"Error loading data from CSV file: {e}")
            raise
    
    @staticmethod
    def inspect_datatypes(df: pd.DataFrame) -> Dict[str, str]:
        """
        Inspect the data types of each column in the DataFrame.
        
        Args:
            df: DataFrame to inspect
            
        Returns:
            Dictionary mapping column names to their Python data types
        """
        logger.info("Inspecting data types")
        
        # Get the Python data type for each column
        datatypes = {}
        for column in df.columns:
            # Get a non-null value to determine the actual Python type
            sample_values = df[column].dropna()
            if len(sample_values) > 0:
                sample_value = sample_values.iloc[0]
                datatypes[column] = type(sample_value).__name__
            else:
                # If all values are null, use the pandas dtype
                datatypes[column] = str(df[column].dtype)
        
        return datatypes


class TaggingSystem:
    """
    Handles the application of the BIM-inspired tagging system to data fields.
    """
    
    def __init__(self, config_path: str):
        """
        Initialize the tagging system with the configuration file.
        
        Args:
            config_path: Path to the tags configuration file
        """
        self.config = self._load_config(config_path)
        self.semantic_tags = self.config.get('semantic_tags', {})
        self.transformations = self.config.get('transformations', {})
    
    def _load_config(self, config_path: str) -> Dict[str, Any]:
        """
        Load the tagging configuration from a YAML or JSON file.
        
        Args:
            config_path: Path to the configuration file
            
        Returns:
            Dictionary containing the configuration
        """
        logger.info(f"Loading tagging configuration from {config_path}")
        
        file_extension = os.path.splitext(config_path)[1].lower()
        
        try:
            if file_extension == '.yaml' or file_extension == '.yml':
                with open(config_path, 'r') as f:
                    config = yaml.safe_load(f)
            elif file_extension == '.json':
                with open(config_path, 'r') as f:
                    config = json.load(f)
            else:
                raise ValueError(f"Unsupported configuration file format: {file_extension}")
            
            return config
        except Exception as e:
            logger.error(f"Error loading tagging configuration: {e}")
            raise
    
    def tag_fields(self, df: pd.DataFrame, datatypes: Dict[str, str]) -> Dict[str, List[str]]:
        """
        Apply semantic tags to each field in the DataFrame based on keywords and data types.
        
        Args:
            df: DataFrame containing the data
            datatypes: Dictionary mapping column names to their Python data types
            
        Returns:
            Dictionary mapping column names to lists of assigned tags
        """
        logger.info("Applying semantic tags to fields")
        
        field_tags = {}
        
        for column in df.columns:
            column_tags = []
            column_type = datatypes.get(column, 'unknown')
            
            # Check each semantic tag
            for tag_name, tag_config in self.semantic_tags.items():
                keywords = tag_config.get('keywords', [])
                allowed_types = tag_config.get('data_types', [])
                
                # Check if the column name contains any of the keywords
                if any(keyword in column.lower() for keyword in keywords):
                    # Check if the column type is allowed for this tag
                    if not allowed_types or column_type in allowed_types:
                        column_tags.append(tag_name)
            
            field_tags[column] = column_tags
        
        return field_tags


class DataTransformer:
    """
    Handles the application of transformations to data based on tags.
    """
    
    def __init__(self, tagging_system: TaggingSystem):
        """
        Initialize the data transformer with the tagging system.
        
        Args:
            tagging_system: TaggingSystem instance containing transformation rules
        """
        self.tagging_system = tagging_system
        self.transformations = tagging_system.transformations
    
    def transform_data(self, df: pd.DataFrame, field_tags: Dict[str, List[str]]) -> Tuple[pd.DataFrame, Dict[str, Any]]:
        """
        Apply transformations to the data based on field tags.
        
        Args:
            df: DataFrame containing the data
            field_tags: Dictionary mapping column names to lists of assigned tags
            
        Returns:
            tuple: (Transformed DataFrame, transformation metadata)
        """
        logger.info("Applying transformations based on field tags")
        
        # Create a copy of the DataFrame to avoid modifying the original
        transformed_df = df.copy()
        
        # Track transformation metadata
        transformation_metadata = {
            'applied_transformations': {},
            'new_columns': [],
            'dropped_columns': []
        }
        
        # Apply date standardization
        if 'date_standardization' in self.transformations:
            transformed_df, date_meta = self._standardize_dates(
                transformed_df, 
                field_tags, 
                self.transformations['date_standardization']
            )
            if date_meta:
                transformation_metadata['applied_transformations']['date_standardization'] = date_meta
        
        # Apply one-hot encoding
        if 'one_hot_encoding' in self.transformations:
            transformed_df, onehot_meta = self._one_hot_encode(
                transformed_df, 
                field_tags, 
                self.transformations['one_hot_encoding']
            )
            if onehot_meta:
                transformation_metadata['applied_transformations']['one_hot_encoding'] = onehot_meta
                transformation_metadata['new_columns'].extend(onehot_meta.get('new_columns', []))
                transformation_metadata['dropped_columns'].extend(onehot_meta.get('dropped_columns', []))
        
        # Apply numeric normalization
        if 'numeric_normalization' in self.transformations:
            transformed_df, norm_meta = self._normalize_numeric(
                transformed_df, 
                field_tags, 
                self.transformations['numeric_normalization']
            )
            if norm_meta:
                transformation_metadata['applied_transformations']['numeric_normalization'] = norm_meta
        
        return transformed_df, transformation_metadata
    
    def _standardize_dates(
        self, 
        df: pd.DataFrame, 
        field_tags: Dict[str, List[str]], 
        config: Dict[str, Any]
    ) -> Tuple[pd.DataFrame, Dict[str, Any]]:
        """
        Standardize date fields to a consistent format.
        
        Args:
            df: DataFrame containing the data
            field_tags: Dictionary mapping column names to lists of assigned tags
            config: Configuration for date standardization
            
        Returns:
            tuple: (DataFrame with standardized dates, transformation metadata)
        """
        logger.info("Standardizing date fields")
        
        # Get the target format
        date_format = config.get('format', '%Y-%m-%d')
        applies_to_tags = config.get('applies_to_tags', [])
        
        # Track which columns were transformed
        transformed_columns = []
        
        # Create a copy of the DataFrame
        result_df = df.copy()
        
        # Find columns with temporal tags
        for column, tags in field_tags.items():
            if any(tag in applies_to_tags for tag in tags):
                try:
                    # Try to convert to datetime and then to the target format
                    result_df[column] = pd.to_datetime(df[column]).dt.strftime(date_format)
                    transformed_columns.append(column)
                except Exception as e:
                    logger.warning(f"Could not standardize date format for column {column}: {e}")
        
        # Create transformation metadata
        metadata = {
            'transformed_columns': transformed_columns,
            'target_format': date_format
        }
        
        return result_df, metadata if transformed_columns else {}
    
    def _one_hot_encode(
        self, 
        df: pd.DataFrame, 
        field_tags: Dict[str, List[str]], 
        config: Dict[str, Any]
    ) -> Tuple[pd.DataFrame, Dict[str, Any]]:
        """
        Apply one-hot encoding to categorical fields.
        
        Args:
            df: DataFrame containing the data
            field_tags: Dictionary mapping column names to lists of assigned tags
            config: Configuration for one-hot encoding
            
        Returns:
            tuple: (DataFrame with one-hot encoded columns, transformation metadata)
        """
        logger.info("One-hot encoding categorical fields")
        
        # Get configuration
        applies_to_tags = config.get('applies_to_tags', [])
        max_categories = config.get('max_categories', 20)
        
        # Track transformation metadata
        transformed_columns = []
        new_columns = []
        dropped_columns = []
        
        # Create a copy of the DataFrame
        result_df = df.copy()
        
        # Find columns with entity type tags
        for column, tags in field_tags.items():
            if any(tag in applies_to_tags for tag in tags):
                # Check if the column has a reasonable number of categories
                unique_values = df[column].nunique()
                if unique_values <= max_categories:
                    try:
                        # Apply one-hot encoding
                        dummies = pd.get_dummies(df[column], prefix=column)
                        
                        # Add the new columns to the result DataFrame
                        for dummy_col in dummies.columns:
                            result_df[dummy_col] = dummies[dummy_col]
                            new_columns.append(dummy_col)
                        
                        # Drop the original column
                        result_df = result_df.drop(columns=[column])
                        dropped_columns.append(column)
                        
                        transformed_columns.append(column)
                    except Exception as e:
                        logger.warning(f"Could not one-hot encode column {column}: {e}")
                else:
                    logger.warning(f"Column {column} has too many categories ({unique_values}) for one-hot encoding")
        
        # Create transformation metadata
        metadata = {
            'transformed_columns': transformed_columns,
            'new_columns': new_columns,
            'dropped_columns': dropped_columns,
            'max_categories': max_categories
        }
        
        return result_df, metadata if transformed_columns else {}
    
    def _normalize_numeric(
        self, 
        df: pd.DataFrame, 
        field_tags: Dict[str, List[str]], 
        config: Dict[str, Any]
    ) -> Tuple[pd.DataFrame, Dict[str, Any]]:
        """
        Normalize numeric fields to a specified range.
        
        Args:
            df: DataFrame containing the data
            field_tags: Dictionary mapping column names to lists of assigned tags
            config: Configuration for numeric normalization
            
        Returns:
            tuple: (DataFrame with normalized numeric columns, transformation metadata)
        """
        logger.info("Normalizing numeric fields")
        
        # Get configuration
        applies_to_tags = config.get('applies_to_tags', [])
        method = config.get('method', 'min-max')
        target_range = config.get('range', [0, 1])
        
        # Track which columns were transformed
        transformed_columns = []
        normalization_ranges = {}
        
        # Create a copy of the DataFrame
        result_df = df.copy()
        
        # Find columns with quantitative tags
        for column, tags in field_tags.items():
            if any(tag in applies_to_tags for tag in tags):
                try:
                    # Check if the column is numeric
                    if pd.api.types.is_numeric_dtype(df[column]):
                        if method == 'min-max':
                            # Min-max normalization
                            min_val = df[column].min()
                            max_val = df[column].max()
                            
                            # Avoid division by zero
                            if min_val != max_val:
                                result_df[column] = (df[column] - min_val) / (max_val - min_val)
                                
                                # Scale to target range if different from [0, 1]
                                if target_range != [0, 1]:
                                    result_df[column] = result_df[column] * (target_range[1] - target_range[0]) + target_range[0]
                                
                                transformed_columns.append(column)
                                normalization_ranges[column] = {
                                    'original_range': [float(min_val), float(max_val)],
                                    'target_range': target_range
                                }
                            else:
                                logger.warning(f"Column {column} has constant value, skipping normalization")
                        
                        elif method == 'z-score':
                            # Z-score normalization
                            mean_val = df[column].mean()
                            std_val = df[column].std()
                            
                            # Avoid division by zero
                            if std_val > 0:
                                result_df[column] = (df[column] - mean_val) / std_val
                                
                                transformed_columns.append(column)
                                normalization_ranges[column] = {
                                    'mean': float(mean_val),
                                    'std': float(std_val)
                                }
                            else:
                                logger.warning(f"Column {column} has zero standard deviation, skipping normalization")
                    else:
                        logger.warning(f"Column {column} is not numeric, skipping normalization")
                except Exception as e:
                    logger.warning(f"Could not normalize column {column}: {e}")
        
        # Create transformation metadata
        metadata = {
            'transformed_columns': transformed_columns,
            'method': method,
            'target_range': target_range,
            'normalization_ranges': normalization_ranges
        }
        
        return result_df, metadata if transformed_columns else {}


class MetadataManager:
    """
    Handles the management of metadata for transformed datasets.
    """
    
    @staticmethod
    def attach_metadata(
        df: pd.DataFrame, 
        original_metadata: Dict[str, Any],
        field_tags: Dict[str, List[str]],
        transformation_metadata: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Attach metadata to a transformed dataset.
        
        Args:
            df: DataFrame containing the transformed data
            original_metadata: Original metadata from the processed file
            field_tags: Dictionary mapping column names to lists of assigned tags
            transformation_metadata: Metadata about the applied transformations
            
        Returns:
            Dictionary containing the data and metadata
        """
        logger.info("Attaching metadata to transformed dataset")
        
        # Create enriched metadata
        enriched_metadata = original_metadata.copy()
        
        # Update basic metadata
        enriched_metadata.update({
            'transformation_timestamp': datetime.now().isoformat(),
            'row_count': len(df),
            'column_count': len(df.columns),
            'columns': list(df.columns)
        })
        
        # Add tagging and transformation metadata
        enriched_metadata['field_tags'] = field_tags
        enriched_metadata['transformations'] = transformation_metadata
        
        # Add tag descriptions
        tag_descriptions = {}
        for tag_name, tag_info in TaggingSystem(TAGS_CONFIG_PATH).semantic_tags.items():
            if 'description' in tag_info:
                tag_descriptions[tag_name] = tag_info['description']
        
        enriched_metadata['tag_descriptions'] = tag_descriptions
        
        # Create payload with data and metadata
        payload = {
            'metadata': enriched_metadata,
            'data': df.to_dict(orient='records')
        }
        
        return payload


class DataForwarder:
    """
    Handles the forwarding (saving) of transformed data to the destination.
    """
    
    @staticmethod
    def forward_to_enriched(payload: Dict[str, Any], original_filename: str) -> str:
        """
        Forward the transformed data to the enriched directory.
        
        Args:
            payload: Dictionary containing the data and metadata
            original_filename: Name of the original source file
            
        Returns:
            Path to the saved file
        """
        # Ensure the enriched directory exists
        os.makedirs(ENRICHED_DATA_DIR, exist_ok=True)
        
        # Get the base filename without extension
        base_filename = os.path.splitext(os.path.basename(original_filename))[0]
        
        # Create the output filename
        output_filename = os.path.join(ENRICHED_DATA_DIR, f"{base_filename}.json")
        
        logger.info(f"Forwarding transformed data to {output_filename}")
        
        # Save the payload as JSON
        with open(output_filename, 'w') as f:
            json.dump(payload, f, indent=2)
        
        return output_filename


class TransformationLogger:
    """
    Handles logging of transformation operations.
    """
    
    @staticmethod
    def initialize_log():
        """
        Initialize the transformation log file if it doesn't exist.
        """
        # Ensure the logs directory exists
        os.makedirs(LOGS_DIR, exist_ok=True)
        
        # Check if the log file exists
        if not os.path.exists(TRANSFORMATION_LOG_PATH):
            logger.info(f"Creating transformation log file: {TRANSFORMATION_LOG_PATH}")
            
            # Create the log file with headers
            with open(TRANSFORMATION_LOG_PATH, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow([
                    'timestamp',
                    'filename',
                    'source_format',
                    'row_count',
                    'column_count',
                    'applied_tags',
                    'applied_transformations',
                    'status',
                    'output_path'
                ])
    
    @staticmethod
    def log_transformation(
        filename: str,
        source_format: str,
        row_count: int,
        column_count: int,
        field_tags: Dict[str, List[str]],
        transformation_metadata: Dict[str, Any],
        status: str,
        output_path: str
    ):
        """
        Log a transformation operation to the transformation log file.
        
        Args:
            filename: Name of the processed file
            source_format: Format of the source file
            row_count: Number of rows in the dataset
            column_count: Number of columns in the dataset
            field_tags: Dictionary mapping column names to lists of assigned tags
            transformation_metadata: Metadata about the applied transformations
            status: Status of the transformation (success or error)
            output_path: Path to the output file
        """
        # Ensure the log file exists
        TransformationLogger.initialize_log()
        
        # Format the field tags for logging
        applied_tags = ';'.join([f"{col}:{','.join(tags)}" for col, tags in field_tags.items() if tags])
        
        # Format the transformation metadata for logging
        applied_transformations = ';'.join([
            f"{name}:{','.join(meta.get('transformed_columns', []))}"
            for name, meta in transformation_metadata.get('applied_transformations', {}).items()
            if meta.get('transformed_columns')
        ])
        
        # Log the transformation
        with open(TRANSFORMATION_LOG_PATH, 'a', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([
                datetime.now().isoformat(),
                filename,
                source_format,
                row_count,
                column_count,
                applied_tags,
                applied_transformations,
                status,
                output_path
            ])


class FileEventHandler(FileSystemEventHandler):
    """
    Handles file system events for the watchdog observer.
    """
    
    def __init__(self):
        """Initialize the file event handler."""
        self.tagging_system = TaggingSystem(TAGS_CONFIG_PATH)
        self.data_transformer = DataTransformer(self.tagging_system)
    
    def on_created(self, event):
        """
        Handle file creation events.
        
        Args:
            event: File system event
        """
        if not event.is_directory:
            file_path = event.src_path
            file_extension = os.path.splitext(file_path)[1].lower()
            
            # Only process CSV and JSON files
            if file_extension in ['.csv', '.json']:
                logger.info(f"New file detected: {file_path}")
                self._process_file(file_path)
    
    def _process_file(self, file_path: str):
        """
        Process a new file.
        
        Args:
            file_path: Path to the file to process
        """
        try:
            # Load data from the file
            df, metadata = DataLoader.load_from_file(file_path)
            
            # Inspect data types
            datatypes = DataLoader.inspect_datatypes(df)
            
            # Apply semantic tags
            field_tags = self.tagging_system.tag_fields(df, datatypes)
            
            # Apply transformations
            transformed_df, transformation_metadata = self.data_transformer.transform_data(df, field_tags)
            
            # Attach metadata
            payload = MetadataManager.attach_metadata(
                transformed_df,
                metadata,
                field_tags,
                transformation_metadata
            )
            
            # Forward to enriched directory
            output_path = DataForwarder.forward_to_enriched(
                payload,
                os.path.basename(file_path)
            )
            
            # Log the transformation
            TransformationLogger.log_transformation(
                os.path.basename(file_path),
                metadata.get('source_format', 'unknown'),
                len(df),
                len(df.columns),
                field_tags,
                transformation_metadata,
                'success',
                output_path
            )
            
            logger.info(f"File processed successfully: {file_path} -> {output_path}")
            
        except Exception as e:
            logger.error(f"Error processing file {file_path}: {e}")
            
            # Log the error
            try:
                TransformationLogger.log_transformation(
                    os.path.basename(file_path),
                    'unknown',
                    0,
                    0,
                    {},
                    {},
                    f'error: {str(e)}',
                    ''
                )
            except Exception as log_error:
                logger.error(f"Error logging transformation: {log_error}")


class TransformationAgent:
    """
    Main class for the Transformation Agent.
    """
    
    def __init__(self):
        """Initialize the Transformation Agent."""
        # Ensure the necessary directories exist
        os.makedirs(PROCESSED_DATA_DIR, exist_ok=True)
        os.makedirs(ENRICHED_DATA_DIR, exist_ok=True)
        os.makedirs(LOGS_DIR, exist_ok=True)
        os.makedirs(CONFIG_DIR, exist_ok=True)
        
        # Initialize the transformation log
        TransformationLogger.initialize_log()
        
        self.observer = Observer()
        self.event_handler = FileEventHandler()
    
    def start(self):
        """Start monitoring the processed data directory."""
        logger.info(f"Starting to monitor directory: {PROCESSED_DATA_DIR}")
        
        # Schedule the observer to watch the processed data directory
        self.observer.schedule(self.event_handler, PROCESSED_DATA_DIR, recursive=False)
        self.observer.start()
        
        try:
            # Process any existing files in the directory
            self._process_existing_files()
            
            # Keep the main thread alive
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            logger.info("Stopping the observer due to keyboard interrupt")
            self.observer.stop()
        
        self.observer.join()
    
    def _process_existing_files(self):
        """Process any existing files in the processed data directory."""
        logger.info("Checking for existing files in the processed data directory")
        
        for filename in os.listdir(PROCESSED_DATA_DIR):
            file_path = os.path.join(PROCESSED_DATA_DIR, filename)
            
            # Only process files (not directories)
            if os.path.isfile(file_path):
                file_extension = os.path.splitext(file_path)[1].lower()
                
                # Only process CSV and JSON files
                if file_extension in ['.csv', '.json']:
                    logger.info(f"Processing existing file: {file_path}")
                    
                    # Create a file created event and process it
                    event = FileCreatedEvent(file_path)
                    self.event_handler.on_created(event)


def main():
    """Main entry point for the Transformation Agent."""
    logger.info("Initializing Transformation Agent")
    
    # Create and start the transformation agent
    agent = TransformationAgent()
    agent.start()


if __name__ == "__main__":
    main()
