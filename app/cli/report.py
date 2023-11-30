import itertools
import os
import typing

from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas


def generate_report(data: list[list[str]]) -> None:
    w, h = A4
    x_offset = 50
    y_offset = 80
    padding = 15
    max_rows_per_page = 45
    data = prep_data(data)
    c = canvas.Canvas("report.pdf", pagesize=A4)
    c.setFont("Helvetica-Bold", 14)
    c.drawString(50, h - 50, "All Files Report Table")
    c.setFont("Helvetica", 6)
    xlist = [x + x_offset for x in [0, 100, 160, 220, 280, 340, 400, 460, 520]]
    ylist = [h - y_offset - i * padding for i in range(max_rows_per_page + 1)]
    is_first_row = True
    for rows in grouper(data, max_rows_per_page):
        rows = tuple(filter(bool, rows))
        c.grid(xlist, ylist[: len(rows) + 1])
        for y, row in zip(ylist[:-1], rows):
            for x, cell in zip(xlist, row):
                if is_first_row:
                    c.setFont("Helvetica-Bold", 8)
                    c.drawString(x + 2, y - padding + 3, str(cell))
                    c.setFont("Helvetica", 6)
                    continue
                if x == 510 and not is_first_row:
                    if cell:
                        c.setFillColorRGB(255, 0, 0)
                        c.drawString(x + 2, y - padding + 3, str(cell))
                    else:
                        c.setFillColorRGB(0, 255, 0)
                        c.drawString(x + 2, y - padding + 3, str(cell))
                    c.setFillColorRGB(0, 0, 0)
                    continue
                c.drawString(x + 2, y - padding + 3, str(cell))
            is_first_row = False
        c.showPage()
    c.save()


def grouper(iterable: typing.Iterable[typing.Any], n: int) -> typing.Iterable[typing.Any]:
    args = [iter(iterable)] * n
    return itertools.zip_longest(*args)


def prep_data(data: list[list[typing.Any]]) -> list[tuple[typing.Any, ...]]:
    result = []
    result.append(
        ("FileName", "DateTime Origin", "DateTime", "Software", "Copyright", "Coordinates", "Has Source", "Is Edited")
    )
    for x in data:
        filename = os.path.basename(x[0][0])
        dto = x[0][1][0].strftime("%Y-%m-%d %H:%M:%S") if len(x[0][1]) >= 1 else ""
        dt = x[0][1][1].strftime("%Y-%m-%d %H:%M:%S") if len(x[0][1]) >= 2 else ""
        is_edited_by_date = x[0][1][2] if len(x[0][1]) >= 3 else 0
        soft = x[0][2][0] if len(x[0][2]) >= 1 else ""
        is_edited_by_soft = x[0][2][1] if len(x[0][2]) >= 2 else 0
        coop = x[0][3][0][:23] if len(x[0][3]) >= 1 else ""
        gps = x[0][4][0] if len(x[0][4]) >= 1 else ""
        source = x[0][5][0] if len(x[0][5]) >= 1 else 0
        is_edited = is_edited_by_date or is_edited_by_soft
        result.append((filename, dto, dt, soft, coop, gps, bool(source), bool(is_edited)))
    return result
