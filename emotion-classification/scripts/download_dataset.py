import os
import subprocess
import shutil
import csv

REPO_URL = "https://github.com/google-research/google-research.git"
CHECKOUT_DIR = ".tmp_sparse_checkout"
FILES_IN_REPO = [
    "goemotions/data/train.tsv",
    "goemotions/data/dev.tsv",
    "goemotions/data/test.tsv"
]
DEST_FILE = os.path.join("data", "raw", "emotion_dataset.csv")

def sparse_checkout():
    if os.path.exists(CHECKOUT_DIR):
        shutil.rmtree(CHECKOUT_DIR)
    os.makedirs(os.path.dirname(DEST_FILE), exist_ok=True)
    try:
        subprocess.run(["git", "clone", "--filter=blob:none", "--no-checkout", REPO_URL, CHECKOUT_DIR], check=True)
        subprocess.run(["git", "sparse-checkout", "init", "--cone"], cwd=CHECKOUT_DIR, check=True)
        subprocess.run(["git", "sparse-checkout", "set"] + FILES_IN_REPO, cwd=CHECKOUT_DIR, check=True)
        subprocess.run(["git", "checkout"], cwd=CHECKOUT_DIR, check=True)

        # Combine all TSV files into a single CSV
        header_written = False
        with open(DEST_FILE, "w", encoding="utf-8", newline='') as csv_out:
            writer = None
            for rel_path in FILES_IN_REPO:
                src_file = os.path.join(CHECKOUT_DIR, rel_path)
                with open(src_file, "r", encoding="utf-8") as tsv_in:
                    reader = csv.reader(tsv_in, delimiter="\t")
                    header = next(reader)
                    if not header_written:
                        writer = csv.writer(csv_out)
                        writer.writerow(header)
                        header_written = True
                    for row in reader:
                        writer.writerow(row)
        print(f"Dataset combined and saved as: {DEST_FILE}")
    finally:
        if os.path.exists(CHECKOUT_DIR):
            shutil.rmtree(CHECKOUT_DIR)

if __name__ == "__main__":
    sparse_checkout()
