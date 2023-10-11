import logging
from threading import Thread
import sys

from app.controllers.webserver import start
logging.basicConfig(stream=sys.stdout, level=logging.INFO)

if __name__ == "__main__":
    server_thread = Thread(target=start)
    server_thread.start()
    server_thread.join()
