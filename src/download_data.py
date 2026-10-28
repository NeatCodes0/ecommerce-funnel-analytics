import os
import shutil
import kagglehub

# 1. Download via kagglehub
print("Downloading dataset from Kaggle...")
download_path = kagglehub.dataset_download("mkechinov/ecommerce-events-history-in-cosmetics-shop")
print("Downloaded to cache:", download_path)

# 2. Destination path in our project
target_dir = os.path.abspath("data/raw")
os.makedirs(target_dir, exist_ok=True)

# 3. Identify and copy CSV files over
for file_name in os.listdir(download_path):
    if file_name.endswith(".csv"):
        src_file = os.path.join(download_path, file_name)
        dst_file = os.path.join(target_dir, file_name)
        print(f"Copying {file_name} -> {dst_file}...")
        shutil.copy2(src_file, dst_file)

print("\nFiles in data/raw/:")
for f in os.listdir(target_dir):
    size_mb = os.path.getsize(os.path.join(target_dir, f)) / (1024 * 1024)
    print(f" - {f} ({size_mb:.2f} MB)")