import threading
import time
import uuid

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

    random_text = 'This is a random text with emoji 🤔'
    encoded_text = random_text.encode()
    identity = 'random_text'

    client.upload_content(encoded_text, identity)

    # Повторной загрузки файла не произойдет, если файл не изменялся
    client.upload_content(encoded_text, identity)

    downloaded = client.download_content(identity)

    assert encoded_text == downloaded


if __name__ == '__main__':
    main()
