import os
import typing as t
from pathlib import Path

import rich
import typer
from PIL import ExifTags, Image

from app.cli.ela import generate_ela
from app.cli.inspectors import (
    inspect_copyright,
    inspect_datetime_fields,
    inspect_editing_software,
    inspect_gps,
    inspect_osx_metadata,
)
from app.cli.utils import (
    TMP_FOLDER,
    download_images,
    filter_images_from_paths,
    print_error_and_exit,
    print_header,
    print_list_item,
    print_sub_header,
    print_success, is_osxmetadata_package_present,
)

app = typer.Typer()

EDITING_SOFTWARE_TAG_PARTS = [
    "GIMP",
    "Photoshop",
]

PathAnnotation = t.Annotated[
    Path,
    typer.Option(
        exists=True,
        file_okay=True,
        dir_okay=False,
        writable=False,
        readable=True,
        resolve_path=True,
    ),
]


@app.command(
    help="Cleans all the files that were added during the scanning, e.g. downloaded images from the URL",
)
def clean() -> None:
    """To be implemented"""


def scan_image(path: PathAnnotation | str) -> None:
    print_header(f"Started scanning image {path}")

    img = Image.open(path)
    if raw_exif := img._getexif():
        exif = {ExifTags.TAGS[k]: v for k, v in raw_exif.items() if k in ExifTags.TAGS}
        inspect_datetime_fields(exif)
        inspect_editing_software(exif)
        inspect_copyright(exif)
        inspect_gps(exif)
    else:
        rich.print("No exif metadata fields found!\n")

    inspect_osx_metadata(path)
    print_header(f"Finished scanning image {path}")


def scan_path(path: PathAnnotation | str) -> None:
    if os.path.isdir(path):
        print_header(f"Scanning directory {path}")

        paths = os.listdir(path)
        img_paths = filter_images_from_paths(paths)
        for img_path in img_paths:
            scan_image(f"{path}/{img_path}")
    else:
        scan_image(path)


@app.command(
    help="Run the Error Level Analysis (ELA) scan",
)
def ela(path: PathAnnotation) -> None:
    if not os.path.exists(path):
        print_error_and_exit("file does not exist under the specified path!")

    generate_ela(str(path))

    print_success("ELA images were successfully generated!")


@app.command(
    help="Run the metadata fields analysis scan",
)
def scan(
    path: PathAnnotation | None = None,
    url: t.Optional[str] = None,
) -> None:
    if not path and not url:
        print_error_and_exit("--path or --url param is required!")

    if path and url:
        print_error_and_exit("only one of the --path or --url params should be specified!")

    print_header(f"Started image scanner")
    print_sub_header("The following features will be analysed:")
    print_list_item("exif datetime fields")
    print_list_item("exif editing software fields")
    print_list_item("exif copyright field")
    if is_osxmetadata_package_present():
        print_list_item("osxmetadata fields")

    if path:
        if not os.path.exists(path):
            print_error_and_exit("file or directory does not exist under the specified path!")
        scan_path(path)

    if url:
        download_images(url)
        scan_path(TMP_FOLDER)


if __name__ == "__main__":
    app()
