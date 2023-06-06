import sys
import os
import argparse
from PIL import Image
from PIL.ExifTags import TAGS, GPSTAGS

def parser():
	parser = argparse.ArgumentParser(prog='scorpion', description="Extracts and displays EXIF data from image files and, if displays GPSInfo if possible")
	parser.add_argument('files', nargs='+', help="List of files")
	return parser.parse_args()

def get_exif(file:str):
	data = dict()
	try:
		exif_image = Image.open(file)
	except Exception as e:
		sys.exit(f"Fail to load image from '{file}: {e}")
	exif_data = getattr(exif_image, '_getexif', lambda: None)()
	if exif_data:
		for key, value in exif_data.items():
			decoded = TAGS.get(key, key)
			if decoded == "GPSInfo":
				gps_data = dict()
				for i in value:
					gpstag = GPSTAGS.get(i, i)
					gps_data[gpstag] = value[i]
					print(f" GPSInfo[{gpstag}], value {gps_data[gpstag]}")
				data[decoded] = gps_data
			else:
				print(f" {decoded} : {value}")
				data[decoded] = value
	else:
		print("No EXIF data found in :", file)
	return


if __name__ == "__main__":
	if len(sys.argv) == 1:
		sys.exit("./scorpion FILE1 [FILE2 ...]")
	args = parser()
	files = args.files
	for file in files:
		print()
		print(f" {file} :")
		print()
		exif = get_exif(file)
