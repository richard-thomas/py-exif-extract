# py-exif-extract

Python module/script to extract EXIF metadata from JPEG image files and (optionally) output to a CSV file, or in a prettified format. To simplify usage of location photographs in mapping (or other GIS applications), it will also consolidate any GPS location data found into 2 additional float attributes:

- gps_lat_decimal: latitude (in decimal degress)
- gps_lon_decimal: longitude (in decimal degress)

This module is implemented as a wrapper around the read functions of the third party ["exif"](https://exif.readthedocs.io/) python library.

## Command line usage

```bash
python exif_extract.py [-h] [-p] [-a] [-s] [-o OUTPUT] infile [infile ...]
```

Positional Argument | Description
-- | --
infile | input JPEG image filename(s)

Optional Argument | Description
-- | --
-h, --help | show this help message and exit
-p, --prettyprint | write metadata to stderr in a pretty format
-a, --aliases | use "pretty print" aliases for CSV file headings
-s, --silent | do not write progress to stderr
-o OUTPUT, --output OUTPUT | filename to write CSV metadata output

Example command line usage:

```bash
python exif_extract.py -o exif_output.csv example_images/*
python exif_extract.py -a -o exif_output2.csv "example_images/* inc GPS.jpg"
```

Notes:

1. Filename wildcarding has been added for where it is not natively directly supported (i.e. for Windows Command Prompt or PowerShell).
2. Tested using Python 3.9.4 64-bit in Windows 10 (cmd tool, PowerShell,
Git Bash shell), with JPEG images from devices:
Canon GX5 (camera without GPS) and Sony XZ2 (phone with GPS).

## Python module usage

Example Python module usage:

```python
import exif_extract
a = exif_extract.ExifExtract(["example_images/DSC_0101 - EXIF inc GPS.jpg",
    "example_images/DSC_0158 - EXIF inc GPS.jpg"])
a.write_csv(open('exif_output.csv', 'w'))
```

This module is used by instantiating objects of a single class `ExifExtract`, from which data attributes can be directly read, or manipulated with by 2 methods `write_csv()` or `pretty_print_exif()`.

### Class `ExifExtract(infilenames, verbose=False)`

Extract all EXIF metadata from specified JPEG image files.

Argument | Type | Description
-- | -- | --
`infilenames` | list of strings | input JPEG image filenames
`verbose` | bool | List files to stderr as they are processed

Resulting class instance data attributes:

Attribute | Type | Description
-- | -- | --
`field_headings` | list of strings | aggregated list of metadata field headings found in all files
`exif_table` | list of dictionaries | metadata extracted from each file (keys from `field_headings`)
`pretty_aliases` | dictionary of strings | prettified version of each field heading

The type of each `exif_table` dictionary value is defined in the ["exif" library Data Types](https://exif.readthedocs.io/en/latest/api_reference.html#data-types) documentation.

Raises:

- exception `ExtractError`: call to underlying "exif" library metadata extraction failed

### Method: `write_csv(outfile, use_aliases=False)`

Write EXIF metadata in Comma Separated Variable (CSV) format.

Argument | Type | Description
-- | -- | --
outfile | file object | destination for writing text
use_aliases | bool | use prettified aliases for CSV headings

### Method: `pretty_print_exif(single_image_exif, outfile=sys.stdout)`

Pretty Print EXIF metadata for a single image.

Argument | Type | Description
-- | -- | --
single_image_exif | dictionary | a single list element from `exif_table` representing EXIF data for 1 image
outfile | file object | print output file (default = stdout)

## Licence

MIT - see [LICENCE](LICENSE).

## Acknowledgements

The heart of this module/script is the "exif" package (Copyright 2021 Tyler N. Thieding): more information at [Gitlab](https://gitlab.com/TNThieding/exif) and [ReadTheDocs](https://exif.readthedocs.io/).

Thanks to the following article for an introduction and code examples for using the "exif" package: [Medium: How to extract GPS coordinates from Images in Python](https://medium.com/spatial-data-science/how-to-extract-gps-coordinates-from-images-in-python-e66e542af354).
