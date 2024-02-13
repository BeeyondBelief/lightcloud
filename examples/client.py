import tempfile
import threading
import time
import uuid
from pathlib import Path

from lightcloud_client.client import CloudClient


def run_server_in_background():
    from lightcloud.main import app
    import uvicorn
    uvicorn.run(app, host='127.0.0.1', port=8000)


def main():
    threading.Thread(target=run_server_in_background, daemon=True).start()
    time.sleep(0.5)

    token = uuid.UUID('91b26497-9389-4f72-b4ff-53ba4913e801')
    client = CloudClient('http://127.0.0.1:8000', token)

    random_text = 'This is a random text'
    path = Path(tempfile.gettempdir()) / 'random.txt'

    path.write_text(random_text)

    client.upload_file(path)

    # Повторной загрузки файла не произойдет, если файл не изменялся
    client.upload_file(path)

    client.download_file(path, path)

    assert path.read_text() == random_text

    path.unlink()


if __name__ == '__main__':
    main()
