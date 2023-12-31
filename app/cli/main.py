import os
import typing
import typing as t
import warnings
from pathlib import Path

import typer
from PIL import ExifTags, Image

from app.cli.inspectors import (
    inspect_copyright,
    inspect_datetime_fields,
    inspect_editing_software,
    inspect_gps,
    inspect_osx_metadata,
)
from app.cli.report import generate_report
from app.utils import (
    DOWNLOAD_TMP_FOLDER,
    clean_temp_folders_and_files,
    download_images,
    filter_images_or_directories_from_paths,
    is_osxmetadata_package_present,
    print_error_and_exit,
    print_header,
    print_list_item,
    print_sub_header,
    create_temp_folders,
)
from app.ela_nn.ela import check_ela
from app.ela_nn.model import IMDModel

warnings.filterwarnings("ignore")

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
    clean_temp_folders_and_files()


def scan_image(path: typing.Union[PathAnnotation, str]) -> list[str]:
    result = []
    result.append(path)
    img = Image.open(path)
    if raw_exif := img._getexif():
        exif = {ExifTags.TAGS[k]: v for k, v in raw_exif.items() if k in ExifTags.TAGS}
        result.append(inspect_datetime_fields(exif))
        result.append(inspect_editing_software(exif))
        result.append(inspect_copyright(exif))
        result.append(inspect_gps(exif))

    result.append(inspect_osx_metadata(path))
    return result


def scan_path(path: t.Union[PathAnnotation, str]) -> list[list[str]]:
    result = []
    if os.path.isdir(path):
        paths = os.listdir(path)
        child_paths = filter_images_or_directories_from_paths(path, paths)
        for child_path in child_paths:
            result.append(scan_path(f"{path}/{child_path}"))
        return result
    else:
        result.append(scan_image(path))
        return result


@app.command(
    help="Run the ELA (Error Level Analysis) scan",
)
def ela(path: PathAnnotation) -> None:
    create_temp_folders()

    if not os.path.exists(path):
        print_error_and_exit("file does not exist under the specified path!")

    check_ela(str(path))

    clean_temp_folders_and_files()


@app.command(
    help="Run the metadata fields analysis scan",
)
def scan(
    path: t.Optional[PathAnnotation] = None,
    url: t.Optional[str] = None,
) -> None:
    if not path and not url:
        print_error_and_exit("--path or --url param is required!")

    if path and url:
        print_error_and_exit("only one of the --path or --url params should be specified!")

    print_header("Started image scanner")
    print_sub_header("The following features will be analysed:")
    print_list_item("exif datetime fields")
    print_list_item("exif editing software fields")
    print_list_item("exif copyright field")
    print_list_item("GPS fields\n")

    if is_osxmetadata_package_present():
        print_list_item("osxmetadata fields")

    create_temp_folders()

    if path:
        if not os.path.exists(path):
            print_error_and_exit("file or directory does not exist under the specified path!")
        result = scan_path(path)
        generate_report(result)
    if url:
        download_images(url)
        result = scan_path(DOWNLOAD_TMP_FOLDER)
        generate_report(result)

    clean_temp_folders_and_files()

    print_header("Finished image scanner")


if __name__ == "__main__":
    app()
