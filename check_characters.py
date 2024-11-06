import os
import csv
from pathlib import Path
from difflib import SequenceMatcher

def get_mismatch_type(csv_name, actual_name):
    csv_path = Path(csv_name)
    actual_path = Path(actual_name)
    
    # Check exact match first
    if csv_name == actual_name:
        return None, None
        
    # Check extension difference
    if csv_path.suffix.lower() != actual_path.suffix.lower():
        return "extension", f"Change CSV from '{csv_name}' to '{actual_name}'"
    
    # Check capitalization difference
    if csv_name.lower() == actual_name.lower():
        return "capitalization", f"Change CSV from '{csv_name}' to '{actual_name}'"
    
    return "name", f"Change CSV from '{csv_name}' to '{actual_name}'"

def check_character_filenames():
    images_dir = Path("video_app/static/video_app/images/characters")
    csv_dir = Path("video_app/static/video_app/characters")
    
    # Get all image files recursively
    actual_files = set()
    for subdir in images_dir.glob("**/*"):
        if subdir.is_file() and subdir.suffix.lower() in ['.png', '.jpg', '.webp', '.svg']:
            actual_files.add((
                subdir.name,
                subdir.stem.lower(),
                subdir.parent.name
            ))
    
    print(f"Total image files found: {len(actual_files)}")
    
    # Track different types of issues
    extension_issues = []
    capitalization_issues = []
    name_issues = []
    missing_files = []
    
    # Check all CSV files
    csv_files = list(csv_dir.glob("*.csv"))
    print(f"CSV files found: {len(csv_files)}")
    
    if not csv_files:
        print("\nNo CSV files found to check against.")
        return
    
    for csv_file in csv_files:
        with open(csv_file, 'r', encoding='utf-8') as f:
            csv_reader = csv.DictReader(f)
            for row in csv_reader:
                if 'filename' not in row:
                    print(f"Warning: CSV {csv_file.name} missing 'filename' column")
                    continue
                
                referenced_file = row['filename']
                referenced_stem = Path(referenced_file).stem.lower()
                
                # Check if file exists in any subfolder
                file_found = False
                for actual_file, actual_stem, folder in actual_files:
                    if referenced_stem == actual_stem:
                        file_found = True
                        mismatch_type, message = get_mismatch_type(referenced_file, actual_file)
                        if mismatch_type == "extension":
                            extension_issues.append(f"In {csv_file.name}: {message}")
                        elif mismatch_type == "capitalization":
                            capitalization_issues.append(f"In {csv_file.name}: {message}")
                        elif mismatch_type == "name":
                            name_issues.append(f"In {csv_file.name}: {message}")
                        break
                
                if not file_found:
                    missing_files.append(f"In {csv_file.name}: File '{referenced_file}' not found in any image directory")
    
    # Print results by category
    print("\nRequired CSV Changes:")
    if extension_issues:
        print(f"\nExtension Fixes ({len(extension_issues)}):")
        for issue in extension_issues:
            print(f"- {issue}")
    
    if capitalization_issues:
        print(f"\nCapitalization Fixes ({len(capitalization_issues)}):")
        for issue in capitalization_issues:
            print(f"- {issue}")
    
    if name_issues:
        print(f"\nName Fixes ({len(name_issues)}):")
        for issue in name_issues:
            print(f"- {issue}")
    
    if missing_files:
        print(f"\nMissing Files ({len(missing_files)}):")
        for issue in missing_files:
            print(f"- {issue}")
    
    if not any([extension_issues, capitalization_issues, name_issues, missing_files]):
        print("\nAll filenames match correctly!")

if __name__ == "__main__":
    check_character_filenames()
