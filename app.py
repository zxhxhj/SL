import subprocess
import time
import sys
import os

script_to_run = "se.py"

# 4 hours in seconds (4 hours * 60 minutes * 60 seconds)
restart_interval_seconds = 4 * 60 * 60

process = None

def start_script():
    global process
    if not os.path.exists(script_to_run):
        print(f"Error: File '{script_to_run}' not found in the current directory.")
        print("Please ensure this script is in the same directory as the target application.")
        sys.exit(1)

    print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Starting {script_to_run}...")
    process = subprocess.Popen([sys.executable, script_to_run])
    print(f"Process started successfully. PID: {process.pid}")

def stop_script():
    global process
    if process:
        print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Stopping process {process.pid}...")
        process.kill()
        process.wait() 
        process = None
        print("Process stopped successfully.")

if __name__ == "__main__":
    try:
        while True:
            start_script()
            
            print(f"Process will run for {restart_interval_seconds / 3600} hours.")
            print(f"Next restart scheduled at: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time() + restart_interval_seconds))}")
            
            time.sleep(restart_interval_seconds)
            
            stop_script()
            
            print("--- New Cycle ---")

    except KeyboardInterrupt:
        print("\nInterrupt received (Ctrl+C).")
        stop_script()
        print("Launcher closed.")
        sys.exit(0)
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        stop_script()
        sys.exit(1)

