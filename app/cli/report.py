import itertools
import os

from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas


def generateReport(data):
    w, h = A4
    x_offset = 50
    y_offset = 80
    padding = 15
    max_rows_per_page = 45
    data = prepData(data)
    c = canvas.Canvas("report.pdf", pagesize=A4)
    c.setFont("Helvetica-Bold", 14)
    c.drawString(50, h - 50, "All Files Report Table")
    c.setFont("Helvetica", 6)
    xlist = [x + x_offset for x in [0, 100, 160, 220, 280, 340, 400, 460, 520]]
    ylist = [h - y_offset - i*padding for i in range(max_rows_per_page + 1)]
    isFirstRow = True
    for rows in grouper(data, max_rows_per_page):
        rows = tuple(filter(bool, rows))
        c.grid(xlist, ylist[:len(rows) + 1])
        for y, row in zip(ylist[:-1], rows):
            for x, cell in zip(xlist, row):
                if (isFirstRow):
                    c.setFont("Helvetica-Bold", 8)
                    c.drawString(x + 2, y - padding + 3, str(cell))
                    c.setFont("Helvetica", 6)
                    continue
                if (x == 510 and not isFirstRow):
                    if (cell):
                        c.setFillColorRGB(255, 0, 0)
                        c.drawString(x + 2, y - padding + 3, str(cell))
                    else:
                        c.setFillColorRGB(0, 255, 0)
                        c.drawString(x + 2, y - padding + 3, str(cell))
                    c.setFillColorRGB(0, 0, 0)
                    continue
                c.drawString(x + 2, y - padding + 3, str(cell))
            isFirstRow = False
        c.showPage()
    c.save()


def grouper(iterable, n):
    args = [iter(iterable)] * n
    return itertools.zip_longest(*args)


def prepData(data):
    result = []
    result.append(("FileName", "DateTime Origin", "DateTime", "Software",
                  "Copyright", "Coordinates", "Has Source", "Is Edited"))
    for x in data:
        filename = os.path.basename(x[0])
        dto = x[1][0].strftime("%Y-%m-%d %H:%M:%S") if len(x[1]) >= 1 else ""
        dt = x[1][1].strftime("%Y-%m-%d %H:%M:%S") if len(x[1]) >= 2 else ""
        isEditedByDate = x[1][2] if len(x[1]) >= 3 else 0
        soft = x[2][0] if len(x[2]) >= 1 else ""
        isEditedBySoft = x[2][1] if len(x[2]) >= 2 else 0
        coop = x[3][0][:23] if len(x[3]) >= 1 else ""
        gps = x[4][0] if len(x[4]) >= 1 else ""
        source = x[5][0] if len(x[5]) >= 1 else 0
        isEdited = isEditedByDate or isEditedBySoft
        result.append((filename, dto, dt, soft, coop,
                      gps, bool(source), bool(isEdited)))
    return result
