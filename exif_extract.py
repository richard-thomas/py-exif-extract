#!/usr/bin/python
"""
Extract EXIF metadata from JPEG image files and (optionally) output in CSV or
prettified format

Extract EXIF data using "exif" python library and consolidate any GPS location
data found into 2 additional fields:
  gps_lat_decimal: latitude (in decimal degress)
  gps_lon_decimal: longitude (in decimal degress)
Can be imported as a Python module or run directly as a command line script.

Author: Richard Thomas
Public Repository: https://github.com/richard-thomas/py-exif-extract

Command line usage:
  python exif_extract.py [-h] [-p] [-a] [-s] [-o OUTPUT] infile [infile ...]

positional arguments:
  infile                input JPEG image filename(s)

optional arguments:
  -h, --help            show this help message and exit
  -p, --prettyprint     write metadata to stderr in a pretty format
  -a, --aliases         use "pretty print" aliases for CSV file headings
  -s, --silent          do not write progress to stderr
  -o OUTPUT, --output OUTPUT
                        filename to write CSV metadata output

Example command line usage:
  python exif_extract.py -o exif_output.csv example_images/*
  python exif_extract.py -a -o exif_output2.csv "example_images/* inc GPS.jpg"

Example Python module usage:
    import exif_extract
    a = exif_extract.ExifExtract(["example_images/DSC_0101 - EXIF inc GPS.jpg",
        "example_images/DSC_0158 - EXIF inc GPS.jpg"])
    a.write_csv(open('exif_output.csv', 'w'))

Notes:
  1. Tested using Python 3.9.4 64-bit in Windows 10 (cmd tool, PowerShell,
     Git Bash shell), with JPEG images from devices:
     Canon GX5 (camera without GPS) and Sony XZ2 (phone with GPS).

Copyright (c) 2022 Richard Thomas
MIT Licence (https://choosealicense.com/licenses/mit/)
"""

from exif import Image
import argparse
import glob
import sys

class ExifExtract:
    """Reading and processing of EXIF metadata from image files."""

    class ExtractError(Exception):
        """Exception Type: EXIF metadata extraction failed."""

        def __init__(self):
            self.message = (
                "EXIF metadata extraction failed!"
            )

    def __init__(self, infilenames, verbose=False):
        """
        Parse all EXIF metadata from specified JPEG image files.

        Args:
            infilenames: array of input JPEG image filenames
        Args (optional):
            verbose: (bool) List files to stderr as they are processed
        Raises:
            ExtractError: EXIF metadata extraction failed
        """

        def gps_decimal_coords(coords, ref):
            """Convert EXIF GPS coordinate encoding to a decimal number."""

            decimal_degrees = coords[0] + coords[1] / 60 + coords[2] / 3600
            if ref == "S" or ref == "W":
                decimal_degrees = -decimal_degrees
            return decimal_degrees

        self.exif_table = []
        field_headings = ['filename','gps_lat_decimal','gps_lon_decimal']
        for path_name in infilenames:
            if verbose:
                sys.stderr.write("Reading file: %s\n" % path_name)

            with open(path_name, 'rb') as file:
                try:
                    image_bytes = file.read()
                    my_image = Image(image_bytes)
                except Exception:
                    raise ExifExtract.ExtractError

            if not my_image.has_exif:
                if verbose:
                    sys.stderr.write("- No EXIF metadata found - skipping file\n")
                continue

            # Extract just EXIF data
            image_exif_data = {'filename': path_name}
            for key in dir(my_image):
                image_exif_data[key] = my_image.get(key)

            # Calculate consolidated lat/lon decimal fields (including signs)
            if 'gps_latitude' in image_exif_data:
                image_exif_data['gps_lat_decimal'] = gps_decimal_coords(
                    image_exif_data['gps_latitude'],
                    image_exif_data['gps_latitude_ref'])
            if 'gps_longitude' in image_exif_data:
                image_exif_data['gps_lon_decimal'] = gps_decimal_coords(
                    image_exif_data['gps_longitude'],
                    image_exif_data['gps_longitude_ref'])

            self.exif_table += [image_exif_data]

            # Add any new EXIF fields found in this file to existing field list
            # (Keep the order where possible - new fields added at the end)
            # Method depends on ordered dictionaries in Python 3.7+:
            # https://stackoverflow.com/questions/12897374/get-unique-values-from-a-list-in-python
            field_headings = list(dict.fromkeys(field_headings +
                list(image_exif_data)))

        self.field_headings = field_headings

        # Convert field headings to a more human readable form
        self.pretty_aliases = {}
        for key in self.field_headings:
            self.pretty_aliases[key] = (key.replace('_', ' ').title()
                .replace("Gps", "GPS").replace("Jpeg", "JPEG")
                .replace("Exif", "EXIF")).replace("Id", "ID")
        self.pretty_aliases['gps_lat_decimal'] = "GPS Latitude  (decimal degrees)"
        self.pretty_aliases['gps_lon_decimal'] = "GPS Longitude (decimal degrees)"

    def write_csv(self, outfile, use_aliases=False):
        """
        Write EXIF metadata in Comma Separated Variable (CSV) format.

        Args:
            outfile: file object opened for writing text
        Args (optional):
            use_aliases: use prettified aliases for CSV headings
        """

        # Write field name header line to output file
        if use_aliases:
            aliases = [self.pretty_aliases[key] for key in self.field_headings]
            outfile.write(','.join(aliases) + '\n')
        else:
            outfile.write(','.join(self.field_headings) + '\n')

        # Write body lines (1 per input file containing EXIF data).
        for row in self.exif_table:
            csv_fields = []
            for key in self.field_headings:
                # If field missing for any file, then empty field (just a comma).
                field = str(row.get(key, ''))

                # Double up any double quotes in the field
                field = field.replace('"', '""')

                # If field has "," characters then put it all in double quotes
                if ',' in field:
                    field = '"' + field + '"'
                csv_fields += [str(field)]

            outfile.write(','.join(csv_fields) + '\n')

    def pretty_print_exif(self, single_image_exif, outfile=sys.stdout):
        """
        Pretty Print EXIF metadata for a single image.

        Args:
            single_image_exif: dictionary of EXIF data for an image
        Args (optional):
            outfile: print output file (default = stdout)
        """

        for key in self.field_headings:
            value = single_image_exif.get(key)
            if value and key != "filename":
                outfile.write(self.pretty_aliases[key] + ": " + str(value) + "\n")

# ------------------------------------------------------------------------------
# Handle if called as a command line script
# (And as an example of how to invoke class methods from an importing module)
# ------------------------------------------------------------------------------

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description="Extract EXIF metadata from JPEG image files and (optionally) output in CSV or prettified format",
        epilog="""Also consolidates any GPS location data found into 2 additional fields:
  gps_lat_decimal: latitude (in decimal degress)
  gps_lon_decimal: longitude (in decimal degress)"""
    )
    parser.add_argument(
        "-p",
        "--prettyprint",
        action="store_true",
        help="write metadata to stderr in a pretty format",
    )
    parser.add_argument(
        "-a",
        "--aliases",
        action="store_true",
        help='use "pretty print" aliases for CSV file headings',
    )
    parser.add_argument(
        "-s",
        "--silent",
        action="store_true",
        help="do not write progress to stderr",
    )
    parser.add_argument(
        "infile",
        nargs="+",
        help="input JPEG image filenames",
    )
    parser.add_argument(
        "-o",
        "--output",
        type=argparse.FileType("w"),
        help="filename to write CSV metadata output",
    )
    args = parser.parse_args()

    # Perform wildcard expansion on input file names & ensure at least one
    # of the specified files exists
    infile_list = []
    for filepath in args.infile:
        infile_list += glob.glob(filepath)
    if len(infile_list) == 0:
        sys.stderr.write("ERROR: no input files found\n")
        sys.exit(1)

    # Extract EXIF data from all files
    try:
        exif_data = ExifExtract(infile_list, not args.silent)
    except ExifExtract.ExtractError as error:
        sys.stderr.write("ERROR: %s\n" % error.message)
        sys.exit(1)

    # If nothing specified then default to CSV output sent to console
    if not (args.output or args.prettyprint):
        args.prettyprint = True

    # If requested pretty each file's EXIF metadata
    if args.prettyprint:
        for single_image_exif in exif_data.exif_table:
            sys.stdout.write("""
------------------------------------------------------------------------------
FILE: %s
------------------------------------------------------------------------------
""" % single_image_exif['filename'])
            exif_data.pretty_print_exif(single_image_exif)

    # Write to CSV file
    if args.output:
        if not args.silent:
            sys.stderr.write("Writing extracted EXIF metadata to CSV file: %s\n"
                % args.output.name)

        # Write EXIF metadata to a single CSV file
        exif_data.write_csv(args.output, args.aliases)
        if (args.output not in [sys.stdout, sys.stdin]):
            args.output.close()



