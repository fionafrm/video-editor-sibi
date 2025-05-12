import os
import requests

folder_path = r"C:\Users\Fiona Ratu Maheswari\Documents\Kerjaan eui\Asdos\video-riset"  # Ubah ke path folder yang diinginkan
url = "http://127.0.0.1:8000/upload_video/"

folder_name = "29_Januari_2020"
count = 1

for file_name in os.listdir(folder_path):
    if file_name.endswith(".mp4"):  # Only upload files with .mp4
        file_path = os.path.join(folder_path, file_name)
        
        video_title = f"{count:04d}"
        with open(file_path, "rb") as file:
            files = {"file": file}
            data = {
                "folder_name": folder_name,
                "video_title": video_title
            }
            response = requests.post(url, files=files, data=data)
            
            # Print the response from the server
            print(f"Uploaded: {file_name} -> {response.json()}")

        count += 1
