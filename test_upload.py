import requests
import uuid
import time
import os

url = "http://127.0.0.1:5001/create"
myid = str(uuid.uuid4())

# Ensure we have the test image
if not os.path.exists("test_image.jpg"):
    from PIL import Image
    Image.new('RGB', (100, 100), color = 'blue').save('test_image.jpg')

with open("test_image.jpg", "rb") as f:
    files = {'file1': ('test_image.jpg', f, 'image/jpeg')}
    data = {'uuid': myid, 'text': 'This is a test reel from python.'}
    
    print("Submitting POST to /create...")
    response = requests.post(url, files=files, data=data, allow_redirects=False)

print(f"Status Code: {response.status_code}")
print(f"Headers Location: {response.headers.get('Location')}")

time.sleep(1) # wait for bg thread
gallery_response = requests.get("http://127.0.0.1:5001/gallery")

if myid in gallery_response.text:
    print(f"✅ SUCCESS: {myid} found in gallery HTML")
else:
    print(f"❌ ERROR: {myid} NOT found in gallery HTML")
