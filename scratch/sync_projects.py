import os
import shutil

src_dir = "c:/Users/SVI/Desktop/Disease Predictor using Machine Learning - Copy - Copy"
dest_dirs = [
    "c:/Users/SVI/Desktop/Disease Predictor using Machine Learning - Copy",
    "c:/Users/SVI/Desktop/Disease Predictor using Machine Learning"
]

files_to_sync = [
    "templates/homepage/index.html",
    "templates/basic.html",
    "templates/patient/checkdisease/checkdisease.html"
]

print("Starting synchronization...")

for dest in dest_dirs:
    if os.path.exists(dest):
        print(f"Syncing to sibling: {dest}")
        for rel_path in files_to_sync:
            src_file = os.path.join(src_dir, rel_path)
            dest_file = os.path.join(dest, rel_path)
            
            # Create subdirs in destination if not existing
            os.makedirs(os.path.dirname(dest_file), exist_ok=True)
            
            # Copy file
            shutil.copy2(src_file, dest_file)
            print(f"  Copied {rel_path}")
    else:
        print(f"Sibling directory does not exist: {dest}")

print("Synchronization complete!")
