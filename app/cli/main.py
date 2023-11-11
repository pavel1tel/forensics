import typing as t
from pathlib import Path

import rich
import typer
from PIL import ExifTags, Image

from app.cli.checkers import check_datetime_fields, check_editing_software, check_osx_metadata

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


@app.command()
def scan(
    path: PathAnnotation | None = None,
    url: str | None = None,
) -> None:
    if not path and not url:
        raise ValueError("--path or --url param is required!")

    if path:
        img = Image.open(path)
        if raw_exif := img._getexif():
            exif = {ExifTags.TAGS[k]: v for k, v in raw_exif.items() if k in ExifTags.TAGS}
            check_datetime_fields(exif)
            check_editing_software(exif)
        else:
            rich.print("No exif metadata fields found!\n")

        check_osx_metadata(path)


if __name__ == "__main__":
    app()
