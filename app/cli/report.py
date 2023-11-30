import itertools
import os
import typing
from PIL import Image, ImageChops
import collections
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
import matplotlib.pyplot as plt
import numpy as np

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
    xlist = [x + x_offset for x in [0, 100, 160, 220, 280, 340, 420, 470, 520]]
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
                if x == 520 and not is_first_row:
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
        c.setFont("Helvetica", 6)
    edited = create_chart_of_eddited_data(data)
    c.setFont("Helvetica-Bold", 14)
    c.drawString(50, h - 50, "Edited Files Pie chart")
    c.setFont("Helvetica", 10)
    c.drawString(50, h - 65, "Edited: " + str(edited) + " Original: " + str(len(data) - edited))
    c.drawImage("temp/editedChart.png", -100, h - 550)
    create_Years_chart(data)
    c.drawImage("temp/yearBar.png", 0, 50)
    c.save()

def create_chart_of_eddited_data(data):
    countEdited = 0
    labels = ["Edited", "Original"]
    colors = ["Red", "green"]
    for el in data[1::]:
        if(el[7]):
            countEdited += 1
    y = np.array([countEdited, len(data) - countEdited])
    plt.pie(y, labels=labels, colors=colors)
    plt.savefig("temp/editedChart.png")
    getCountryFromCoordinates(data)
    return countEdited

def create_Years_chart(data):
    dictt = {}
    for item in data[1:]:
        date = item[1]
        if(date != ""):
            year = date[:4]
            if(year in dictt):
                dictt[year] = dictt[year] + 1
            else:
                dictt[year] = 1
    dictt = dict(sorted(dictt.items()))
    years = list(dictt.keys())
    values = list(dictt.values())
    fig = plt.figure(figsize = (10, 5))
    plt.bar(years, values, color ='maroon')
    plt.xlabel("Years")
    plt.ylabel("No. of images made this year")
    plt.title("Images made by year")
    plt.savefig("temp/yearBar.png")
    image = Image.open('temp/yearBar.png')
    image.thumbnail((600, 600))
    image.save('temp/yearBar.png')

def getCountryFromCoordinates(data):
    for item in data:
        coords = item[5]
        if(coords != ""):
            print(coords)

def grouper(iterable: typing.Iterable[typing.Any], n: int) -> typing.Iterable[typing.Any]:
    args = [iter(iterable)] * n
    return itertools.zip_longest(*args)


def make_flat(data: list[typing.Any], flat_data: list[typing.Any]) -> None:
    for item in data:
        if not len(item):
            continue

        if isinstance(item[0], str):
            flat_data.append(item)
            continue

        if isinstance(item[0], list):
            make_flat(item, flat_data)
            continue
    return


def get_row(x: list[typing.Any]) -> typing.Any:
    filename = os.path.basename(x[0])
    dto = x[1][0].strftime("%Y-%m-%d %H:%M:%S") if len(x[1]) >= 1 else ""
    dt = x[1][1].strftime("%Y-%m-%d %H:%M:%S") if len(x[1]) >= 2 else ""
    is_edited_by_date = x[1][2] if len(x[1]) >= 3 else 0
    soft = x[2][0][:15] if len(x[2]) >= 1 else ""
    is_edited_by_soft = x[2][1] if len(x[2]) >= 2 else 0
    coop = x[3][0][:12] if len(x[3]) >= 1 else ""
    gps = x[4][0] if len(x[4]) >= 1 else ""
    source = x[5][0] if len(x[5]) >= 1 else 0
    is_edited = is_edited_by_date or is_edited_by_soft
    return (filename, dto, dt, soft, coop, gps, bool(source), bool(is_edited),)


def prep_data(data: list[typing.Any]) -> list[tuple[typing.Any, ...]]:
    flat_data = []
    make_flat(data, flat_data)
    result = []
    result.append(
        ("FileName", "DateTime Origin", "DateTime", "Software", "Copyright", "Coordinates", "Has Source", "Is Edited")
    )
    for x in flat_data:
        try:
            result.append(get_row(x))
        except Exception as e:
            # todo handle error
            pass
    return result
