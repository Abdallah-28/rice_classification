import requests
import io
from PIL import Image

def predict_image(api_url, image: Image.Image):
    """
    Calls the prediction API with the provided image.
    """
    img_bytes = io.BytesIO()
    image.save(img_bytes, format='PNG')
    img_bytes.seek(0)
    
    files = {'file': ('image.png', img_bytes, 'image/png')}
    
    response = requests.post(
        f"{api_url}/predict",
        files=files,
        timeout=30
    )
    
    response.raise_for_status()
    return response.json()
