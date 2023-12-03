# Image scanner

# Usage

## Installation

### 1.1. Install the package using **pip**

```shell
pip install git+https://github.com/pavel1tel/forensics.git
```

### 1.2. Install the package using **poetry**

```shell
poetry add git+https://github.com/pavel1tel/forensics.git
```

### 2. Run setup script 

```shell
$ image_scan_setup
```

### 3. Run scans

```shell
$ image_scan scan --path <path>
```

# Development

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

### 2. Clone the repository
```shell
$ git clone https://github.com/pavel1tel/forensics
```

### 3. Install the dependencies
```shell
$ poetry install
```


### 4. Run setup script 

```shell
$ image_scan_setup
```


## Running example scans

```shell
$ image_scan scan --path app/exif_samples/Canon_40D.jpg

$ image_scan scan --path app/samples/acceptance.jpeg

$ image_scan ela --path app/samples/queen.png

$ image_scan ela --path app/samples/queen2.jpg

$ image_scan scan --path app/exif_samples/gps/DSCN0021.jpg
```
