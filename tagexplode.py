import csv
import ast
import os
import sys
import argparse
import time
import traceback
from io import StringIO

def main():
    parser = argparse.ArgumentParser(description='Process CSV file to explode tag columns')
    parser.add_argument('input_file', help='Path to input CSV file')
    parser.add_argument('-o', '--output', help='Output CSV file path (default: adds _exploded suffix)')
    parser.add_argument('-t', '--tag-columns', default='tags', help='Comma-separated tag column names (default: tags)')
    
    args = parser.parse_args()
    
    # Get tag column names from argument
    TAG_COLUMNS = [col.strip() for col in args.tag_columns.split(',')]
    
    # Determine output file path
    if args.output:
        output_file = args.output
    else:
        base_name = os.path.splitext(args.input_file)[0]
        output_file = f"{base_name}_exploded.csv"
    
    # Cache for parsed tag data to avoid repeated parsing
    tag_cache = {}
    
    try:
        start_time = time.time()
        
        print(f"Processing: {args.input_file}")
        print(f"Output will be written to: {output_file}")
        
        # Function to extract all tags from tags JSON
        def extract_all_tags(tags_str):
            # Use cache to avoid repeated parsing of the same tag string
            if tags_str in tag_cache:
                return tag_cache[tags_str]
                
            try:
                tags_data = ast.literal_eval(tags_str)
                
                # If it's a list, convert to dictionary format
                if isinstance(tags_data, list):
                    tags_dict = {}
                    for item in tags_data:
                        if isinstance(item, dict) and 'key' in item and 'value' in item:
                            tags_dict[item['key']] = str(item['value'])
                else:
                    tags_dict = {k: str(v) for k, v in tags_data.items()}
                
                # Store in cache
                tag_cache[tags_str] = tags_dict
                return tags_dict
            except (ValueError, SyntaxError, TypeError):
                tag_cache[tags_str] = {}
                return {}
        
        # Read the entire file to get all tag names first
        print("Reading file to discover all tag names...")
        with open(args.input_file, 'r', encoding='utf-8') as f:
            file_content = f.read()
        print(f"File size: {len(file_content)} bytes")
        
        # Create CSV reader
        csv_file = StringIO(file_content)
        reader = csv.DictReader(csv_file)
        header = reader.fieldnames
        print(f"CSV header: {header}")
        
        # Discover all tag names
        all_tag_names = set()
        row_count = 0
        for row in reader:
            row_count += 1
            for tag_column in TAG_COLUMNS:
                if tag_column in row and row[tag_column]:
                    try:
                        tags_dict = extract_all_tags(row[tag_column])
                        all_tag_names.update(tags_dict.keys())
                    except Exception as e:
                        print(f"Error discovering tags in row {row_count}: {str(e)}")
        
        print(f"First pass complete. Processed {row_count} rows.")
        print(f"Discovered {len(all_tag_names)} unique tag names: {all_tag_names}")
        
        # Reset file pointer for second pass
        csv_file = StringIO(file_content)  # Create a new StringIO object to avoid issues
        reader = csv.DictReader(csv_file)
        
        # Prepare output file
        output = StringIO()
        # Create sorted list of prefixed tag names
        sorted_tag_names = sorted(all_tag_names)
        prefixed_tag_names = [f"x.{name}" for name in sorted_tag_names]
        
        # Include original columns plus all discovered tag names with 'x.' prefix
        fieldnames = header + prefixed_tag_names
        writer = csv.DictWriter(output, fieldnames=fieldnames)
        writer.writeheader()
        
        # Process rows and write directly
        print("Processing rows and writing output...")
        rows_processed = 0
        
        for row in reader:
            try:
                # Extract tags from each tag column
                for tag_column in TAG_COLUMNS:
                    if tag_column in row and row[tag_column]:
                        try:
                            tags_dict = extract_all_tags(row[tag_column])
                            # Add each tag to the row with 'x.' prefix
                            for tag_name, tag_value in tags_dict.items():
                                row[f"x.{tag_name}"] = tag_value
                        except Exception as e:
                            print(f"Error processing row {rows_processed}, column {tag_column}: {str(e)}")
                
                # Write row directly to output
                writer.writerow(row)
                rows_processed += 1
                
                # Log progress more frequently
                if rows_processed % 500 == 0:
                    print(f"Processed {rows_processed} rows...")
            except Exception as e:
                print(f"Error processing row {rows_processed}: {str(e)}")
                print(f"Row data: {row}")
                traceback.print_exc()
        
        print(f"Second pass complete. Processed {rows_processed} rows.")
        
        # Write processed file to disk
        print(f"Writing output to {output_file}...")
        output_content = output.getvalue()
        print(f"Output size: {len(output_content)} bytes")
        
        with open(output_file, 'w', encoding='utf-8', newline='') as f:
            f.write(output_content)
        
        total_time = time.time() - start_time
        print(f"Processing completed in {total_time:.2f} seconds")
        print(f"File processed successfully: {rows_processed} rows, {len(prefixed_tag_names)} tags discovered")
        print(f"Output saved to: {output_file}")
        
    except Exception as e:
        print(f"Error: {str(e)}")
        print(traceback.format_exc())
        sys.exit(1)

if __name__ == '__main__':
    main()
