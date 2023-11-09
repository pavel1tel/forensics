import datetime
import typing as t

import typer
from PIL import ExifTags, Image
from rich import print

app = typer.Typer()

EDITING_SOFTWARE_TAG_PARTS = [
    "GIMP",
    "Photoshop",
]


@app.command()
def asdf(path: str | None = None, url: str | None = None) -> None:
    if not path and not url:
        raise ValueError("--path or --url param is required!")


def check_datetime_fields(exif: dict[str, t.Any]) -> None:
    print("[green]Checking datetime fields...[/green]")

    # checking datetime original tag
    datetime_format = "%Y:%m:%d %H:%M:%S"
    img_datetime_original = datetime.datetime.strptime(exif["DateTimeOriginal"], datetime_format).astimezone()
    print(f"Image was taken at {img_datetime_original}\n")

    # comparing datetime original and datetime tags
    img_datetime = datetime.datetime.strptime(exif["DateTime"], datetime_format).astimezone()

    if img_datetime != img_datetime_original:
        delta = img_datetime - img_datetime_original
        print(
            f"DateTimeOriginal exif tag doesn't match the DateTime exif tag, it's off by {delta}. "
            f"DateTimeOriginal tag usually contains the information about date and time when the image was made, while "
            f"DateTime tag usually contains the information about the date and time of last image editing. It can "
            f"indicate that [red]image was edited![red]\n",
        )


def check_editing_software(exif: dict[str, t.Any]) -> None:
    print("[green]Checking editing software fields...[/green]")
    for part in EDITING_SOFTWARE_TAG_PARTS:
        if part.lower() in exif["Software"].lower():
            print(
                f"Editing software tag was detected: {exif['Software']}. It can indicate that "
                f"[red]image was edited![red]\n",
            )


@app.command()
def scan(path: str | None = None, url: str | None = None) -> None:
    if not path and not url:
        raise ValueError("--path or --url param is required!")

    img = Image.open(path)
    exif = {ExifTags.TAGS[k]: v for k, v in img._getexif().items() if k in ExifTags.TAGS}
    check_datetime_fields(exif)
    check_editing_software(exif)


if __name__ == "__main__":
    app()
