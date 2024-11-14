import os
import time
import logging
import shutil
import psutil
from collections import Counter
from scipy.stats import entropy
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

file_modifications = []

# Set up logging
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S')

def on_modified(event):
    if event.is_directory:
        return
    modified_file = event.src_path
    modified_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(os.path.getmtime(modified_file)))
    logging.info(f"File modified: {modified_file}, Modified Time: {modified_time}")

    file_modifications.append((modified_file, modified_time))

    # Check file similarity
    original_file = modified_file.replace("Backup", "Protectit")  # Assuming the original file is in the Protectit folder
    if file_similarity(original_file, modified_file):
        logging.info(f"File similarity check passed for: {modified_file}")
    else:
        logging.warning(f"File similarity check failed for: {modified_file}")
        add_tmp_extension(modified_file)

def add_tmp_extension(file_path):
    if not file_path.endswith(".tmp"):
        new_file_path = file_path + ".tmp"
        os.rename(file_path, new_file_path)
        logging.warning(f"Added .tmp extension to file: {file_path}")

def backup_original_files(monitored_folder, backup_folder):
    try:
        if not os.path.exists(backup_folder):
            os.makedirs(backup_folder)

        for root, _, files in os.walk(monitored_folder):
            for file_name in files:
                file_path = os.path.join(root, file_name)
                backup_file_path = os.path.join(backup_folder, file_name)
                shutil.copy2(file_path, backup_file_path)

                logging.info(f"Original file backed up: {file_path}")
    except Exception as e:
        logging.error(f"Error backing up original files: {e}")

def monitor_folder(folder_path, backup_folder):
    backup_original_files(folder_path, backup_folder)
    create_honey_pot_folder()

    event_handler = FileSystemEventHandler()
    event_handler.on_modified = on_modified

    observer = Observer()
    observer.schedule(event_handler, folder_path, recursive=True)
    observer.start()
    
    try:
        print("Monitoring folder for potential ransomware activity...")
        while True:
            while True:
                cpu_percent = psutil.cpu_percent(interval=1)
                disk_percent = psutil.disk_usage('/').percent

            # Check if CPU or disk usage exceeds threshold
                if cpu_percent > 80 or disk_percent > 80:
                    logging.warning(f"High CPU or disk usage detected. CPU: {cpu_percent}%, Disk: {disk_percent}%")

                    print("High CPU or disk usage detected. System will restart shortly.")
                    os.system("shutdown /r /t 1")  # Restart system after 1 second

                # Check for file modifications over time
                check_file_modifications()

            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
        observer.join()
    except Exception as e:
        print(f"An error occurred: {e}")
        observer.stop()
        observer.join()

def calculate_entropy(file_path):
    with open(file_path, 'rb') as f:
        data = f.read()
    _, counts = zip(*sorted(Counter(data).items()))
    prob = [x / sum(counts) for x in counts]
    return entropy(prob)

def file_similarity(original_file, modified_file, threshold=0.1):
    original_entropy = calculate_entropy(original_file)
    modified_entropy = calculate_entropy(modified_file)
    entropy_difference = abs(original_entropy - modified_entropy)
    if entropy_difference > threshold:
        print("Alert: The entropy difference exceeds the threshold. Potential risk of ransomware.")
    return entropy_difference < threshold

def protect_folder_read_only(folder_path):
    for root, _, files in os.walk(folder_path):
        for filename in files:
            file_path = os.path.join(root, filename)
            try:
                os.chmod(file_path, 0o444)
            except OSError as e:
                raise OSError(f"Error setting {file_path} to read-only: {e}")
            
def check_file_modifications():
    global file_modifications
    current_time = time.time()
    recent_modifications = [mod for mod in file_modifications if current_time - mod[1] <= 30]  # Check modifications in last 30 seconds
    if len(recent_modifications) >= 3:
        logging.warning(f"Multiple file modifications detected in the last 30 seconds: {len(recent_modifications)}")
        create_honey_pot_folder()

def find_high_resource_processes():
    processes = []
    for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
        processes.append(proc.info)
    high_cpu_processes = [proc for proc in processes if proc['cpu_percent'] > 80]  # Check processes with CPU usage > 80%
    high_memory_processes = [proc for proc in processes if proc['memory_percent'] > 80]  # Check processes with memory usage > 80%
    if high_cpu_processes:
        logging.warning(f"High CPU usage processes: {high_cpu_processes}")
    if high_memory_processes:
        logging.warning(f"High memory usage processes: {high_memory_processes}")

def create_honey_pot_folder(folder_path=None):
    honey_pot_path = "H:\\recycler\\a\\b\\c\\d\\e\\f\\g\\h"
    if not os.path.exists(honey_pot_path):
        os.makedirs(honey_pot_path)
        logging.info(f"Honey pot folder created: {honey_pot_path}")
    if folder_path:
        move_files_to_honey_pot(folder_path)

def move_files_to_honey_pot(folder_path):
    honey_pot_path = "H:\\recycler\\a\\b\\c\\d\\e\\f\\g\\h"
    for root, _, files in os.walk(folder_path):
        for filename in files:
            file_path = os.path.join(root, filename)
            if not filename.endswith(".tmp"):
                new_file_path = os.path.join(honey_pot_path, filename + ".tmp")
                shutil.move(file_path, new_file_path)
                logging.warning(f"Moved file to honey pot folder: {new_file_path}")

if __name__ == "__main__":
    folder_to_monitor = "H:\\Protectit"
    backup_folder = "H:\\Backup"
    monitor_folder(folder_to_monitor, backup_folder)
    folder_to_protect = "H:\\Protectit"
    protect_folder_read_only(folder_to_protect)
    move_files_to_honey_pot(folder_to_protect)
    print(f"Files in folder set to read-only (to the best effort): {folder_to_protect}")