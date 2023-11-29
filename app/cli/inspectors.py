import datetime
import typing as t
from pathlib import Path

import rich
import typer
import platform

from app.cli.utils import print_header, print_warning

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
    print_header("Analysing datetime fields")
    datetime_format = "%Y:%m:%d %H:%M:%S"

    if "DateTimeOriginal" not in exif:
        return

    img_datetime_original = datetime.datetime.strptime(exif["DateTimeOriginal"], datetime_format).astimezone()
    rich.print(f"Image was taken at {img_datetime_original}\n")

    if "DateTime" not in exif:
        return

    # comparing datetime original and datetime tags
    img_datetime = datetime.datetime.strptime(exif["DateTime"], datetime_format).astimezone()

    if img_datetime != img_datetime_original:
        delta = img_datetime - img_datetime_original
        rich.print(
            f"DateTimeOriginal exif tag doesn't match the DateTime exif tag, it's off by {delta}. "
            f"DateTimeOriginal tag usually contains the information about date and time when the image was made, while "
            f"DateTime tag usually contains the information about the date and time of last image editing. It can "
            f"indicate that [red]image was edited![red]",
        )


@inspector_wrapper
def inspect_editing_software(exif: dict[str, t.Any]) -> None:
    print_header("Analysing editing software fields")
    for part in EDITING_SOFTWARE_TAG_PARTS:
        if part.lower() in exif["Software"].lower():
            rich.print(
                f"Editing software tag was detected: {exif['Software']}. It can indicate that "
                f"[red]image was edited![/red]",
            )
            return
    print_warning("No editing software fields present")


@inspector_wrapper
def inspect_copyright(exif: dict[str, t.Any]) -> None:
    print_header("Analysing copyright field")
    if copyright_ := exif.get("Copyright"):
        rich.print(f"Copyright tag is present with the value {copyright_}\n")
    else:
        print_warning("No copyright tags present")


def _format_coord(parts: tuple[t.Any]) -> str:
    casted_parts = [float(i) for i in parts]
    return f"{casted_parts[0]:.2f}°{casted_parts[1]:.2f}'{casted_parts[2]:.2f}\""


@inspector_wrapper
def inspect_gps(exif: dict[str, t.Any]) -> None:
    print_header("Analysing GPS fields")
    if gps := exif.get("GPSInfo"):
        gps_parts = [v for _, v in gps.items()][:4]
        rich.print(
            f"Coordinates: "
            f"{gps_parts[0]}: {_format_coord(gps_parts[1])} {gps_parts[2]}: {_format_coord(gps_parts[3])} ",
        )
    else:
        print_warning("No GPS fields present")


@inspector_wrapper
def inspect_osx_metadata(path: PathAnnotation | str) -> None:
    print_header("Analysing osxmetadata fields")

    if platform.system() == "Darwin":
        try:
            from osxmetadata import OSXMetaData
        except ImportError:
            print_warning(
                "To perform the OSX specific fields analysis install the full "
                "version of the package with `osxmetadata` dependency"
            )
            return
    else:
        return

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
    else:
        print_warning("No kMDItemWhereFroms tag present")
