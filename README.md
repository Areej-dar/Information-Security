# Ransomware Detection and Protection System

This project is a Python-based system designed to detect and protect against ransomware attacks. It utilizes file monitoring, resource usage analysis, and entropy checks to identify suspicious activity, safeguard data, and respond promptly to potential threats.

## 📚 Features

1. **File Monitoring and Guarding**:
   - Monitors changes in file integrity using SHA-256 hash and entropy calculations.
   - Moves suspicious files to a secure backup directory and makes them read-only.

2. **Resource Monitoring**:
   - Tracks CPU and disk usage in real-time using the `psutil` library.
   - Detects anomalies such as high CPU and disk usage that may indicate ransomware activity.

3. **Ransomware Detection**:
   - Uses file modification patterns and entropy changes to identify ransomware-like behavior.
   - Implements a honeypot mechanism by moving compromised files to a protected folder.

4. **Alerting and Response**:
   - Logs all events and system resource usage.
   - Initiates a system restart when high resource usage and multiple suspicious file changes are detected.

## 💻 How to Run

Ensure you have Python installed along with the required libraries:

```bash
pip install watchdog psutil scipy
Place the script and the necessary folders (monitor and backup) in the same directory, then run:
python ransomware_detection.py

## 🛠️ Technologies Used
Python: Core programming language
Watchdog: For monitoring file system events
Psutil: For tracking system resource usage
Scipy: For entropy calculation

## 📝 Future Improvements
Integration of machine learning models for advanced threat detection.
Real-time behavioral analysis to detect new ransomware patterns.
Centralized dashboard for system monitoring and management.
