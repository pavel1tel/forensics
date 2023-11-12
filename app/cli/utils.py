import os

import rich
import typer
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from PIL import Image
from io import BytesIO

IMAGE_EXTENSIONS = [".png", ".jpg", ".jpeg"]
TMP_FOLDER = "./tmp/"
DOWNLOAD_CHUNK_SIZE = 8192


def print_error_and_exit(msg: str) -> None:
    rich.print(f"[red]{msg}[/red]")
    raise typer.Exit(code=1)


def print_warning(msg: str) -> None:
    rich.print(f"[orange]{msg}[/orange]")


def print_header(msg: str) -> None:
    rich.print(f"\n[green]{msg}[/green]\n")


def filter_images_from_paths(paths: list[str]) -> list[str]:
    return [path for path in paths if any(path.endswith(ext) for ext in IMAGE_EXTENSIONS)]


def get_images_from_url(url: str) -> list[str]:
    response = requests.get(url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        img_tags = soup.find_all('img')
        potential_img_urls = [urljoin(url, img_tag['src']) for img_tag in img_tags]
        return filter_images_from_paths(potential_img_urls)
    else:
        print_error_and_exit(f"Failed to retrieve the webpage. Status code: {response.status_code}")


#
# def download_image(url: str) -> str:
#     img_name = url.split("/")[-1]
#     save_path = TMP_FOLDER + img_name
#
#     response = requests.get(url, stream=True)
#     if response.status_code != 200:
#         print_warning(f"Failed to download image. Status code: {response.status_code}")
#
#     with open(save_path, 'wb') as file:
#         for chunk in response.iter_content(chunk_size=DOWNLOAD_CHUNK_SIZE):
#             file.write(chunk)
#
#     return save_path

def download_image(url: str) -> str:
    img_name = url.split("/")[-1]
    save_path = TMP_FOLDER + img_name

    response = requests.get(url)
    if response.status_code != 200:
        print_warning(f"Failed to download image. Status code: {response.status_code}")

    img = Image.open(BytesIO(response.content))
    if exif := img.info.get("exif"):
        print("Exif !! ", exif)
        img.save(save_path, exif=img.info.get("exif"))
    else:
        img.save(save_path)

    return save_path


def download_images(url: str, limit: int = 10) -> list[str]:
    img_urls = get_images_from_url(url)
    img_paths = []

    if not os.path.exists(TMP_FOLDER):
        os.makedirs(TMP_FOLDER)

    for img_url in img_urls[:limit]:
        img_path = download_image(img_url)
        img_paths.append(img_path)

    return img_paths


if __name__ == '__main__':
    download_images("https://www.vu.lt/")
