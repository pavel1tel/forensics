import datetime
import platform
import typing as t
from pathlib import Path

import typer

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


def inspector_wrapper(f):
    def inner(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except Exception:
            return []

    return inner


@inspector_wrapper
def inspect_datetime_fields(exif: dict[str, t.Any]) -> list[datetime.datetime | int]:
    result = []
    # checking datetime original tag
    datetime_format = "%Y:%m:%d %H:%M:%S"

    if "DateTimeOriginal" not in exif:
        return result
    img_datetime_original = datetime.datetime.strptime(exif["DateTimeOriginal"], datetime_format).astimezone()
    result.append(img_datetime_original)

    if "DateTime" not in exif:
        return result

    # comparing datetime original and datetime tags
    img_datetime = datetime.datetime.strptime(exif["DateTime"], datetime_format).astimezone()
    result.append(img_datetime)

    today = datetime.datetime.today().astimezone(tz=None)

    if img_datetime > today or img_datetime_original > today:

        result.append(1)
        return result

    if img_datetime != img_datetime_original:
        result.append(1)
        return result
    result.append(0)
    return result


@inspector_wrapper
def inspect_editing_software(exif: dict[str, t.Any]) -> list[str]:
    result = []
    for part in EDITING_SOFTWARE_TAG_PARTS:
        if part.lower() in exif["Software"].lower():
            result.append(exif["Software"])
            result.append(1)
            return result
    return []


@inspector_wrapper
def inspect_copyright(exif: dict[str, t.Any]) -> list[str]:
    result = []
    if copyright_ := exif.get("Copyright"):
        result.append(copyright_)
        return result
    else:
        return result


def _format_coord(parts: tuple[t.Any]) -> str:
    casted_parts = [float(i) for i in parts]
    return f"{casted_parts[0]:.2f}°{casted_parts[1]:.2f}'{casted_parts[2]:.2f}\""


@inspector_wrapper
def inspect_gps(exif: dict[str, t.Any]) -> list[str]:
    result = []
    if gps := exif.get("GPSInfo"):
        gps_parts = [v for _, v in gps.items()][:4]
        result.append(f"{gps_parts[0]}: {_format_coord(gps_parts[1])}\n {gps_parts[2]}: {_format_coord(gps_parts[3])} ")
        return result
    else:
        return result


@inspector_wrapper
def inspect_osx_metadata(path: PathAnnotation | str) -> list[str | int]:
    result = []
    if platform.system() == "Darwin":
        try:
            from osxmetadata import OSXMetaData
        except ImportError:
            return result
    else:
        return result

    md = OSXMetaData(str(path))
    md_dict = md.asdict()
    if md_dict["kMDItemWhereFroms"]:
        result.append(1)
        return result
    else:
        return result
