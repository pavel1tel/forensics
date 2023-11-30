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
            return []

    return inner


# result -> {?DateTimeOriginal[Date], ?DateTime[Date], ?isEdited[0 || 1]}
@inspector_wrapper
def inspect_datetime_fields(exif: dict[str, t.Any]) -> None:
    result = []
    # checking datetime original tag
    print_header("Analysing datetime fields")
    datetime_format = "%Y:%m:%d %H:%M:%S"

    if "DateTimeOriginal" not in exif:
        return result
    img_datetime_original = datetime.datetime.strptime(exif["DateTimeOriginal"], datetime_format).astimezone()
    rich.print(f"Image was taken at {img_datetime_original}\n")
    result.append(img_datetime_original)

    if "DateTime" not in exif:
        return result

    # comparing datetime original and datetime tags
    img_datetime = datetime.datetime.strptime(exif["DateTime"], datetime_format).astimezone()
    result.append(img_datetime)

    if img_datetime != img_datetime_original:
        delta = img_datetime - img_datetime_original
        rich.print(
            f"DateTimeOriginal exif tag doesn't match the DateTime exif tag, it's off by {delta}. "
            f"DateTimeOriginal tag usually contains the information about date and time when the image was made, while "
            f"DateTime tag usually contains the information about the date and time of last image editing. It can "
            f"indicate that [red]image was edited![red]",
        )
        result.append(1)
        return result
    result.append(0)
    return result


# result -> {?Software[String], ?isEdited[0 || 1]}
@inspector_wrapper
def inspect_editing_software(exif: dict[str, t.Any]):
    result = []
    print_header("Analysing editing software fields")
    for part in EDITING_SOFTWARE_TAG_PARTS:
        if part.lower() in exif["Software"].lower():
            result.append(exif["Software"])
            rich.print(
                f"Editing software tag was detected: {exif['Software']}. It can indicate that "
                f"[red]image was edited![/red]",
            )
            return result
    print_warning("No editing software fields present")
    return []

#result -> {?Copyright[String]}
@inspector_wrapper
def inspect_copyright(exif: dict[str, t.Any]) -> None:
    result = []
    print_header("Analysing copyright field")
    if copyright_ := exif.get("Copyright"):
        result.append(copyright_)
        rich.print(f"Copyright tag is present with the value {copyright_}\n")
        return result
    else:
        print_warning("No copyright tags present")
        return result


def _format_coord(parts: tuple[t.Any]) -> str:
    casted_parts = [float(i) for i in parts]
    return f"{casted_parts[0]:.2f}°{casted_parts[1]:.2f}'{casted_parts[2]:.2f}\""

#result -> {?Coord[String]} 
@inspector_wrapper
def inspect_gps(exif: dict[str, t.Any]) -> None:
    result = []
    print_header("Analysing GPS fields")
    if gps := exif.get("GPSInfo"):
        gps_parts = [v for _, v in gps.items()][:4]
        rich.print(
            f"Coordinates: "
            f"{gps_parts[0]}: {_format_coord(gps_parts[1])} {gps_parts[2]}: {_format_coord(gps_parts[3])} ",
        )
        result.append(f"{gps_parts[0]}: {_format_coord(gps_parts[1])} {gps_parts[2]}: {_format_coord(gps_parts[3])} ")
        return result
    else:
        print_warning("No GPS fields present")
        return result

#result -> {?hasSource[1]} 
@inspector_wrapper
def inspect_osx_metadata(path: PathAnnotation | str) -> None:
    result = []
    print_header("Analysing osxmetadata fields")

    if platform.system() == "Darwin":
        try:
            from osxmetadata import OSXMetaData
        except ImportError:
            print_warning(
                "To perform the OSX specific fields analysis install the full "
                "version of the package with `osxmetadata` dependency"
            )
            return result
    else:
        return result

    md = OSXMetaData(str(path))
    md_dict = md.asdict()
    if where_froms := md_dict["kMDItemWhereFroms"]:
        rich.print("'kMDItemWhereFroms' tag was detected with the following sources: ")
        result.append(1)
        for wf in where_froms:
            print(wf)
        rich.print(
            "Check that the source is trusted website, in case the website looks like an untrusted source, it may "
            "indicate that the [red]image was fabricated![/red]",
        )
        return result
    else:
        print_warning("No kMDItemWhereFroms tag present")
        return result
