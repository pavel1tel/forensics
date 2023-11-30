import os
import platform
import shutil
from urllib.parse import urljoin

import requests
import rich
import typer
from bs4 import BeautifulSoup

IMAGE_EXTENSIONS = [".png", ".jpg", ".jpeg"]
TMP_FOLDER = "./tmp"
DOWNLOAD_CHUNK_SIZE = 2**14


def is_osxmetadata_package_present() -> bool:
    if platform.system() == "Darwin":
        try:
            from osxmetadata import OSXMetaData

            return True
        except ImportError:
            return False
    else:
        return False


def _center_in_the_terminal(msg: str) -> str:
    terminal_width, _ = shutil.get_terminal_size()
    return f" {msg} ".center(terminal_width, "=")


def print_error_and_exit(msg: str) -> None:
    rich.print(f"[red]{_center_in_the_terminal(msg)}[/red]")
    raise typer.Exit(code=1)


def print_warning(msg: str) -> None:
    rich.print(f"[yellow]{msg}[/yellow]")


def print_header(msg: str) -> None:
    rich.print(f"\n[green]{_center_in_the_terminal(msg)}[/green]\n")


def print_sub_header(msg: str) -> None:
    rich.print(f"{msg}")


def print_list_item(msg: str) -> None:
    rich.print(f"    - {msg}")


def print_success(msg: str) -> None:
    rich.print(f"[green]{_center_in_the_terminal(msg)}[/green]")


def filter_images_from_paths(paths: list[str]) -> list[str]:
    return [path for path in paths if any(path.endswith(ext) for ext in IMAGE_EXTENSIONS)]


def filter_images_or_directories_from_paths(parent_path: str, paths: list[str]) -> list[str]:
    return [
        path for path in paths
        if any(path.endswith(ext) for ext in IMAGE_EXTENSIONS) or os.path.isdir(f"{parent_path}/{path}")
    ]


def get_images_from_url(url: str) -> list[str]:  # type: ignore[return]
    response = requests.get(url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, "html.parser")
        img_tags = soup.find_all("img")
        potential_img_urls = [urljoin(url, img_tag["src"]) for img_tag in img_tags]
        return filter_images_from_paths(potential_img_urls)
    else:
        print_error_and_exit(f"Failed to retrieve the webpage. Status code: {response.status_code}")


def download_image(url: str) -> str:
    img_name = url.split("/")[-1]
    save_path = TMP_FOLDER + "/" + img_name

    response = requests.get(url, stream=True)
    if response.status_code != 200:
        print_warning(f"Failed to download image. Status code: {response.status_code}")

    with open(save_path, "wb") as file:
        for chunk in response.iter_content(chunk_size=DOWNLOAD_CHUNK_SIZE):
            file.write(chunk)

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


if __name__ == "__main__":
    download_images("https://www.vu.lt/")
