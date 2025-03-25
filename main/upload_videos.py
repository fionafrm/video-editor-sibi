import os
import requests

folder_path = r"C:\Users\Fiona Ratu Maheswari\Documents\Kerjaan eui\Asdos\video-riset"  # Ubah ke path folder yang diinginkan
url = "http://127.0.0.1:8000/upload_video/"

for file_name in os.listdir(folder_path):
    if file_name.endswith(".mp4"):  # Hanya upload file dengan format .mp4
        file_path = os.path.join(folder_path, file_name)
        with open(file_path, "rb") as file:
            response = requests.post(url, files={"file": file})
            print(f"Uploaded: {file_name} -> {response.json()}")
