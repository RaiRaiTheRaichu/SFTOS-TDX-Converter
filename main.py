import math

from PIL import Image
from io import open
from tkinter import filedialog

import helpers
import logger_utils
import swizzle

images_failed_to_convert = []

def convert_texture(tdx_file):
    with open(tdx_file, mode='rb') as file:
        # Get what we need from the header
        file.seek(int('0x0000004', base=16))
        width = int.from_bytes(file.read(2), byteorder='little')
        height = int.from_bytes(file.read(2), byteorder='little')
        bpp = int.from_bytes(file.read(1), byteorder='little')

        log.debug(f'Width: {width}, Height: {height}, BPP: {bpp} (Required pixels for 8bpp output: {width * height})')

        # Swizzle data
        file.seek(int('0x00000106', base=16))
        swizzle_pattern = int.from_bytes(file.read(1), byteorder='little')
        is_swizzled = False
        is_pal_swizzled = False
        if swizzle_pattern == 1:    # 01 = swizzled, 02 = not swizzled, 08 = swizzled pixels + swizzled palette
            is_swizzled = True
        elif swizzle_pattern == 8:
            is_swizzled = True
            is_pal_swizzled = True
        elif not swizzle_pattern == 2:
            log.warning(f'Unhandled swizzle flag ({swizzle_pattern}. Skipping...)')
            return False

        log.debug(f'Swizzled: {is_swizzled}, Palette swizzled: {is_pal_swizzled}')

        # Palette data
        if is_pal_swizzled:
            log.debug(f'Running palette unswizzle algorithm')
            file.seek(int('0x000001E0', base=16))
            palette = swizzle.unswizzle_palette(file.read(1024))
        else:
            file.seek(int('0x00000160', base=16))
            palette = file.read(1024)

        rgb_palette, alpha_palette = helpers.get_palette(palette, bpp)

        # Pixel data
        if is_pal_swizzled:
            file.seek(int('0x000005E0', base=16))
        else:
            file.seek(int('0x00000560', base=16))

        if bpp == 4:
            log.debug(f'4bpp, reading pixel data')
            pixel_data = file.read(math.floor((width * height) / 2))
        elif bpp == 8:
            log.debug(f'8bpp, reading pixel data')
            pixel_data = file.read(width * height)
        else:
            log.error(f'Error! File is neither 4bpp or 8bpp. Skipping...')
            return False

        # Handle swizzled pixels
        if is_swizzled:
            if bpp == 8:
                log.debug(f'Running 8bpp unswizzle algorithm')
                try:
                    pixel_data = swizzle.unswizzle_i8(width, height, pixel_data)
                except IndexError:
                    log.error(f'Error thrown while unswizzling 8bpp texture. Skipping...')
                    return False
            if bpp == 4:
                log.debug(f'Running 4bpp unswizzle algorithm')
                try:
                    pixel_data = swizzle.unswizzle_i4(width, height, pixel_data)
                except IndexError:
                    log.error(f'Error thrown while unswizzling 4bpp texture. Skipping...')
                    return False

        # Convert 4BPP to 8BPP
        if bpp == 4:
            log.debug(f'4bpp pixel data length: {len(pixel_data)}')
            if not len(pixel_data) == width*height:
                pixel_data = helpers.convert_to_8bpp(pixel_data)

        log.debug(f'8bpp pixel data length: {len(pixel_data)}')
        assert len(pixel_data) == width*height, f'Pixel data does not contain the expected number of pixels for this image!\nExpected: {width*height}, got {len(pixel_data)}'

        # Build converted PNG image
        converted_image = Image.new("P",(width, height))
        converted_image.putdata(pixel_data)
        converted_image.putpalette(rgb_palette)

        # Add transparency/alpha support
        converted_image.convert("RGBA")
        converted_image.info["transparency"] = bytes(alpha_palette)

        # Save the image
        if helpers.get_save_output():
            converted_image.save(f'{filename[:-4]}.png', "PNG")
        else:
            converted_image.show()
        log.debug(f'Converted image successfully written to disk.')
        return True

# ---Main function---
# Logging
log = logger_utils.instantiate_logger()

# File handling
files_to_convert = filedialog.askopenfilenames(filetypes=[('TDX files', "*.tdx")])

if files_to_convert == "NULL":
    exit()

counter = 0
for filename in files_to_convert:
    log.debug(f'Attempting to convert {filename}')
    result = convert_texture(filename)
    if result:
        counter += 1
    else:
        log.error(f'IndexError caught in file {filename}')
        images_failed_to_convert.append(filename)

log.debug(f'Conversion completed. ({counter}/{len(files_to_convert)} files successfully converted.)')

if images_failed_to_convert:
    log.warning(f'Some images failed to convert. A list is displayed below.')
    for img in images_failed_to_convert:
        log.warning(img)