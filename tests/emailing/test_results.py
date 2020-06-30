import requests
from src.image import is_valid_image

from src.gmail.main import get_results

def test_results():
    results = get_results()
    links = results['links']
    images = results['images']

    for link in links:
        response = requests.get(link)
        status_code = str(response.status_code)

        assert status_code[0] == '2' # 2XX

    for image in images:
        is_image = is_valid_image(image)

        assert is_image == True


