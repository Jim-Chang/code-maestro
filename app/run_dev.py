import subprocess
import time

from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer


class ChangeHandler(FileSystemEventHandler):
    def __init__(self):
        super().__init__()
        self.process = None

    def start_server(self):
        if self.process:
            self.process.terminate()
        self.process = subprocess.Popen(["python", "app/main.py"])

    def on_modified(self, event):
        if "code_base" in event.src_path or not event.src_path.endswith(".py"):
            return

        print(f"{event.src_path} has been modified. Restarting app...")
        self.start_server()


if __name__ == "__main__":
    event_handler = ChangeHandler()
    observer = Observer()
    observer.schedule(event_handler, path=".", recursive=True)
    observer.start()
    print("Watching for changes...")

    try:
        event_handler.start_server()  # Start the server initially
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
        if event_handler.process:
            event_handler.process.terminate()
    observer.join()
