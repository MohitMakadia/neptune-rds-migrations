import sys
import subprocess

import Customer
import Worker

def main():
    if len(sys.argv) < 2:
        print("Usage: python script1.py filename")
        return

    filename = sys.argv[1]

    try:
        subprocess.run(["python3", filename], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error running {filename}: {e}")

if __name__ == "__main__":
    main()