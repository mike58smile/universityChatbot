import time
import os

def update_algorithm():
    print("File changed! Updating algorithm...")
    with open("tst.txt", "r") as file:
        data = file.read()
        print(f"New file contents: {data}")

raw_path = "tst.txt"
if __name__ == "__main__":
    # file_path = "tst.txt"
    # last_modified_time = os.path.getmtime(file_path)

    # print("Monitoring file for changes... Press Ctrl+C to stop.")
    # try:
    #     while True:
    #         current_modified_time = os.path.getmtime(file_path)
    #         if current_modified_time != last_modified_time:
    #             last_modified_time = current_modified_time
    #             update_algorithm()
    #         time.sleep(1)  # Check every second
    # except KeyboardInterrupt:
    #     print("\nStopped monitoring.")
    try:
        last_modified_time = os.path.getmtime(raw_path)
        while True:
            print("Monitoring file for changes...")
            current_modified_time = os.path.getmtime(raw_path)
            if current_modified_time != last_modified_time:
                last_modified_time = current_modified_time
                print("FAQ has changed, calculating embedings...")
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nStopped monitoring.")
    
    print("FAQ is up to date")
