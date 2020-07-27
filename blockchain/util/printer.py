import io
import sys
import threading


class Printer:
    def __init__(self, stream: io.TextIOBase = sys.stdout):
        self.stream = stream
        self.lock = threading.Lock()
        self.tasks = []
        return

    def __del__(self):
        for task in self.tasks:
            if task.is_alive():
                task.join()
        return

    def print(self, text: str, end='\n'):
        t = PrintingTask(self, text + end)
        t.start()
        self.tasks.append(t)
        return


class PrintingTask(threading.Thread):
    def __init__(self, printer: Printer, text: str):
        super(PrintingTask, self).__init__()
        self.printer = printer
        self.text = text
        return

    def run(self):
        self.printer.lock.acquire()
        self.printer.stream.write(self.text)
        self.printer.lock.release()
        return
