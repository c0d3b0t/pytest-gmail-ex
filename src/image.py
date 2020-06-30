import requests

def is_valid_image(image_url):
    valid_image_types = ["image/png", "image/jpeg", "image/jpg", "image/gif"]
    image_formats = [item.strip() for item in valid_image_types]
    r = requests.head(image_url)

    return r.headers["content-type"] in image_formats