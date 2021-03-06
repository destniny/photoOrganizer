from PIL import Image
from PIL import ExifTags
import pyheif
import exifread
from PIL.ExifTags import TAGS
from datetime import datetime
import datetime
import time
import os, io, sys

# Helper functions
def timestamp2string(timeStamp): 
    try: 
        d = datetime.datetime.fromtimestamp(timeStamp)
        str1 = d.strftime("%Y:%m:%d %H:%M:%S") # 2015-08-28 16:43:37.283000'
        return str1
    except Exception as e:
        print(e)
        return ''

def get_FileCreateTime(filePath):
    # filePath = unicode(filePath,'utf8')
    t = os.path.getctime(filePath)
    return timestamp2string(os.stat(filePath).st_birthtime)

def rename_files(path, s, file, ext):
    try:
        os.rename(path+file, path+s+ext)
        print("RENAMED", file, s+ext)
    except Exception:
        print('Failed to rename')

def handle_dup(s):
    if s in photos:
        count += 1
        s += "-" + str(count)
        print(s)
        dup_photos.append(s)
    photos.append(s)


# Starting of the main

photos = []
dup_photos = []
count = 0
path = sys.argv[1] + '/'

for file in os.listdir(path): 
    if file.endswith(".heic"):
        print(file)
        try:
            heif_file = pyheif.read_heif(path+file)
        except Exception:
            continue
        for metadata in heif_file.metadata:
            if metadata['type'] == 'Exif':
                fstream = io.BytesIO(metadata['data'][6:])
            exifdata = exifread.process_file(fstream,details=False)
            time = str(exifdata.get("Image DateTime"))
            break
        
        time = datetime.strptime(time, '%Y:%m:%d %H:%M:%S')
        s = time.strftime('%Y-%m-%d %H%M%S')

        print(file, s)

        rename_files(path, s, file, ".heic")

    elif file.endswith(('.jpg', '.JPG', '.jpeg', '.JPEG')):
        image = Image.open(path+file)
        exifdata = image.getexif()
        # print(exifdata)

        # Decode the metadata
        # for key, val in exifdata.items():
        #     if key in ExifTags.TAGS:
        #         print(f'{ExifTags.TAGS[key]}:{val}')

        # Get Exif.Image.DateTime
        data = exifdata.get(306)
        if data == None:
            # if no DateTime is recorded, get file birth time of local system
            # print("no Exif.Image.DateTime")
            data = get_FileCreateTime(path+file)        
        # print(data)

        # decode bytes 
        if isinstance(data, bytes):
            data = data.decode()
        time = datetime.datetime.strptime(data, '%Y:%m:%d %H:%M:%S')
        # print(time)

        # Format time to the output form
        s = time.strftime('%Y-%m-%d--%H-%M-%S')
        
        # handle duplicated timestamp 
        # which is very likely to happen
        # TODO: possible decision on 1. numbering the dup or 2. drop the dup
        # currently using strategy 1
        handle_dup(s)

        print(file, s)
        rename_files(path, s, file, ".jpeg")

# setList = set(photos)
# photos.sort()
# print(photos)
# print(dup_photos)
# print(len(photos), count, len(setList))
