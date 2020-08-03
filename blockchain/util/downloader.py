import threading
import urllib.request


class Downloader(threading.Thread):
    def __init__(self, url: str, filename: str):
        super(Downloader, self).__init__()
        self.url = url
        self.filename = filename
        return

    def run(self):
        f = open(self.filename, 'wb')
        f.write(urllib.request.urlopen(self.url).read())
        f.close()
        return
