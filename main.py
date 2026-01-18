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

        log.debug(f'Width: {width}, Height: {height}, BPP: {bpp}\n(Total required pixels for 8bpp output: {width * height})')

        # Swizzle data
        file.seek(int('0x00000106', base=16))
        swizzle_pattern = int.from_bytes(file.read(1), byteorder='little')
        is_swizzled = False
        if swizzle_pattern == 1:    # 01 = swizzled, 02 = not swizzled
            is_swizzled = True

        log.debug(f'Is swizzled: {is_swizzled}')

        # Palette data
        file.seek(int('0x00000160', base=16))
        rgb_palette, alpha_palette = helpers.get_palette(file.read(1024), bpp)

        # Pixel data
        file.seek(int('0x00000560', base=16))
        if bpp == 4:
            log.debug(f'4bpp, reading pixel data')
            pixel_data = file.read(math.floor((width * height) / 2))
        elif bpp == 8:
            log.debug(f'8bpp, reading pixel data')
            pixel_data = file.read(width * height)
        else:
            log.error(f'Error! File is neither 4bpp or 8bpp. Skipping...')
            images_failed_to_convert.append(tdx_file)
            return

        # Handle swizzled pixels
        if is_swizzled:
            if bpp == 8:
                log.debug(f'Running 8bpp unswizzle algorithm')
                pixel_data = swizzle.unswizzle_i8(width, height, pixel_data)
            if bpp == 4:
                log.debug(f'Running 4bpp unswizzle algorithm')
                pixel_data = swizzle.unswizzle_i4(width, height, pixel_data)

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

# ---Main function---
# Logging
log = logger_utils.instantiate_logger()

# File handling
files_to_convert = filedialog.askopenfilenames(filetypes=[('TDX files', "*.tdx")])

if files_to_convert == "NULL":
    exit()

for filename in files_to_convert:
    convert_texture(filename)

if images_failed_to_convert:
    log.warn(f'Some images failed to convert. A list is displayed below.')
    for img in images_failed_to_convert:
        log.warn(img)