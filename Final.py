import psutil
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import time
import threading
import shutil
import os
import logging
import hashlib
from collections import Counter
from scipy.stats import entropy

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

file_modifications = []
file_hashes = {}  # Global dictionary to store file hashes

def calculate_hash(filepath):
    sha256_hash = hashlib.sha256()
    with open(filepath, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()

def calculate_entropy(file_path):
    with open(file_path, 'rb') as f:
        data = f.read()
    _, counts = zip(*sorted(Counter(data).items()))
    prob = [x / sum(counts) for x in counts]
    return entropy(prob)

class MonitorHandler(FileSystemEventHandler):
    def __init__(self, backup_dir, monitor_dir):
        self.backup_dir = backup_dir
        self.monitor_dir = monitor_dir
        os.makedirs(self.backup_dir, exist_ok=True)
        self.update_file_hashes()

    def update_file_hashes(self):
        for dirpath, dirnames, filenames in os.walk(self.monitor_dir):
            for filename in filenames:
                filepath = os.path.join(dirpath, filename)
                if not filepath.endswith(('~$')):
                    file_hashes[filepath] = calculate_hash(filepath)

    def on_modified(self, event):
        if not event.is_directory:
            self.handle_event(event)

    def handle_event(self, event):
        path = event.src_path
        if os.path.isfile(path) and not path.endswith(('~$')):
            try:
                new_hash = calculate_hash(path)
                old_hash = file_hashes.get(path)
                if new_hash != old_hash:
                    logging.warning(f"File integrity issue detected: {path}")
                    os.chmod(path, 0o444)  # Make file read-only
                    logging.info(f"Read-only mode activated for {path} due to suspected tampering.")
                    add_tmp_extension(path)  # Add .tmp extension to file
                    move_files_to_honey_pot(os.path.dirname(path))  # Move file to honey pot
                file_hashes[path] = new_hash  # Update the hash post-verification
            except PermissionError as e:
                logging.error(f"Permission error for {path}: {e}")

def add_tmp_extension(file_path):
    if not file_path.endswith(".tmp"):
        new_file_path = file_path + ".tmp"
        os.rename(file_path, new_file_path)
        logging.warning(f"Added .tmp extension to file: {file_path}")

def move_files_to_honey_pot(folder_path):
    honey_pot_path = "H:\\recycler\\a\\b\\c\\d\\e\\f\\g\\h"
    for root, _, files in os.walk(folder_path):
        for filename in files:
            file_path = os.path.join(root, filename)
            if not filename.endswith(".tmp"):
                new_file_path = os.path.join(honey_pot_path, filename + ".tmp")
                shutil.move(file_path, new_file_path)
                logging.warning(f"Moved file to honey pot folder: {new_file_path}")

def monitor_high_resource_usage():
    while True:
        for proc in psutil.process_iter(['pid', 'name', 'cpu_percent']):
            if proc.info['name'] != 'System Idle Process' and proc.info['cpu_percent'] > 80:
                logging.warning(f"High CPU usage detected: {proc.info['name']} (PID: {proc.info['pid']})")
                add_tmp_extension(proc.info['name'])  # Add .tmp extension to suspicious process
                move_files_to_honey_pot(os.path.dirname(proc.info['name']))  # Move suspicious process to honey pot
        time.sleep(10)

def main():
    base_path = r"C:\Users\farwa\.virtualenvs\.virtualenvs\new_env\ai311\IS\monitor"
    backup_path = os.path.join(base_path, "backups")
    os.makedirs(base_path, exist_ok=True)
    os.makedirs(backup_path, exist_ok=True)

    event_handler = MonitorHandler(backup_path, base_path)
    observer = Observer()
    observer.schedule(event_handler, base_path, recursive=True)
    observer.start()

    monitor_thread = threading.Thread(target=monitor_high_resource_usage)
    monitor_thread.start()

    try:
        while True:
            cpu_percent = psutil.cpu_percent(interval=1)
            disk_percent = psutil.disk_usage('/').percent

            if cpu_percent > 80 or disk_percent > 80:
                logging.warning(f"High CPU or disk usage detected. CPU: {cpu_percent}%, Disk: {disk_percent}%")
                print("High CPU or disk usage detected. System will restart shortly.")
                os.system("shutdown /r /t 1")  # Restart system after 1 second

            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
        observer.join()
        monitor_thread.join()
        logging.info("Monitoring stopped by user.")

if __name__ == "__main__":
    main()
