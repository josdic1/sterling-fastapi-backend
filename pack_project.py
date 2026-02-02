import os

# --- CONFIGURATION ---
# folders to skip
IGNORE_DIRS = {
    'node_modules', '.git', '__pycache__', 'venv', 'env', 
    '.vscode', 'dist', 'build', 'coverage'
}

# file extensions to skip
IGNORE_EXTENSIONS = {
    '.png', '.jpg', '.jpeg', '.gif', '.ico', '.svg', 
    '.pyc', '.zip', '.tar', '.gz', '.map', '.lock',
    '.woff', '.woff2', '.ttf', '.eot', '.mp3', '.mp4'
}

# specific filenames to skip
IGNORE_FILES = {
    'package-lock.json', 'yarn.lock', '.DS_Store', 'pack_project.py'
}
# ---------------------

def is_text_file(filepath):
    """Simple check to avoid reading binary files"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            f.read(1024)
        return True
    except (UnicodeDecodeError, IOError):
        return False

def pack_files(start_path='.'):
    with open('project_context.txt', 'w', encoding='utf-8') as outfile:
        for root, dirs, files in os.walk(start_path):
            # Modify dirs in-place to skip ignored directories
            dirs[:] = [d for d in dirs if d not in IGNORE_DIRS]
            
            for file in files:
                if file in IGNORE_FILES:
                    continue
                    
                _, ext = os.path.splitext(file)
                if ext.lower() in IGNORE_EXTENSIONS:
                    continue
                
                filepath = os.path.join(root, file)
                
                if is_text_file(filepath):
                    # Write file header
                    outfile.write(f"\n{'='*50}\n")
                    outfile.write(f"FILE: {filepath}\n")
                    outfile.write(f"{'='*50}\n\n")
                    
                    # Write file content
                    try:
                        with open(filepath, 'r', encoding='utf-8') as infile:
                            outfile.write(infile.read())
                    except Exception as e:
                        outfile.write(f"[Error reading file: {e}]")
                    
                    outfile.write("\n")

if __name__ == "__main__":
    pack_files()
    print("Done! All files saved to 'project_context.txt'")