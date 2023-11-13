# Image scanner

## Installation

###  1. Install the [poetry](https://python-poetry.org/)

```shell
# For mac
$ brew install poetry
```

```shell
# For linux
$ apt-get install poetry
```

### 2. Install the dependencies
```shell
$ poetry install
```

## Running example scans

```shell
$ image_scan scan --path app/exif_samples/Canon_40D.jpg

$ image_scan scan --path app/samples/acceptance.jpeg

$ image_scan ela --path app/samples/queen.png

$ image_scan ela --path app/samples/queen2.jpg
```
