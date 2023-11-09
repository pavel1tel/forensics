# Image scanner

## Installation

```shell
$ poetry install
```

## Example

```shell
$ image_scan scan --path app/exif_samples/Canon_40D.jpg

Checking datetime fields...
Image was taken at 2008-05-30 15:56:01

DateTimeOriginal exif tag doesn't match the DateTime exif tag, it's off by 61 days, 18:42:10. DateTimeOriginal tag usually contains the information about date and time when
the image was made, while DateTime tag usually contains the information about the date and time of last image editing. It can indicate that image was edited!

Checking editing software fields...
Editing software tag was detected: GIMP 2.4.5. It can indicate that image was edited!
```
