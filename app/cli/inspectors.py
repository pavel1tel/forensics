import datetime
import typing as t
from pathlib import Path

import rich
import typer
from osxmetadata import OSXMetaData

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

P = t.ParamSpec("P")
R = t.TypeVar("R")


def inspector_wrapper(f: t.Callable[P, R]) -> t.Callable[P, R | None]:
    def inner(*args: P.args, **kwargs: P.kwargs) -> R | None:
        try:
            return f(*args, **kwargs)
        except Exception as e:
            rich.print(f"Error when performing {f.__name__} check", str(e), "\n")
            return None

    return inner


@inspector_wrapper
def inspect_datetime_fields(exif: dict[str, t.Any]) -> None:
    # checking datetime original tag
    datetime_format = "%Y:%m:%d %H:%M:%S"
    img_datetime_original = datetime.datetime.strptime(exif["DateTimeOriginal"], datetime_format).astimezone()
    rich.print(f"Image was taken at {img_datetime_original}\n")

    # comparing datetime original and datetime tags
    img_datetime = datetime.datetime.strptime(exif["DateTime"], datetime_format).astimezone()

    if img_datetime != img_datetime_original:
        delta = img_datetime - img_datetime_original
        rich.print(
            f"DateTimeOriginal exif tag doesn't match the DateTime exif tag, it's off by {delta}. "
            f"DateTimeOriginal tag usually contains the information about date and time when the image was made, while "
            f"DateTime tag usually contains the information about the date and time of last image editing. It can "
            f"indicate that [red]image was edited![red]\n",
        )


@inspector_wrapper
def inspect_editing_software(exif: dict[str, t.Any]) -> None:
    for part in EDITING_SOFTWARE_TAG_PARTS:
        if part.lower() in exif["Software"].lower():
            rich.print(
                f"Editing software tag was detected: {exif['Software']}. It can indicate that "
                f"[red]image was edited![/red]\n",
            )


@inspector_wrapper
def inspect_copyright(exif: dict[str, t.Any]) -> None:
    if copyright_ := exif.get("Copyright"):
        rich.print(f"Copyright tag is present with the value {copyright_}\n")


@inspector_wrapper
def inspect_osx_metadata(path: PathAnnotation | str) -> None:
    md = OSXMetaData(str(path))
    md_dict = md.asdict()

    if where_froms := md_dict["kMDItemWhereFroms"]:
        rich.print("'kMDItemWhereFroms' tag was detected with the following sources: ")
        for wf in where_froms:
            print(wf)
        rich.print(
            "Check that the source is trusted website, in case the website looks like an untrusted source, it may "
            "indicate that the [red]image was fabricated![/red]",
        )
