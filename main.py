from PIL import Image
from io import open
from tkinter import filedialog

import helpers
import swizzle

def convert_texture(tdx_file):
    with open(tdx_file, mode='rb') as file:
        # Get what we need from the header
        file.seek(int('0x0000004', base=16))
        width = int.from_bytes(file.read(2), byteorder='little')
        height = int.from_bytes(file.read(2), byteorder='little')
        bpp = int.from_bytes(file.read(2), byteorder='little')

        # Swizzle data
        file.seek(int('0x00000106', base=16))
        swizzle_pattern = int.from_bytes(file.read(1), byteorder='little')
        is_swizzled = False
        if swizzle_pattern == 1:    # 01 = swizzled, 02 = not swizzled
            is_swizzled = True

        # Palette data
        file.seek(int('0x00000160', base=16))
        rgb_palette, alpha_palette = helpers.get_palette(file.read(1024), bpp)

        # Pixel data
        file.seek(int('0x00000560', base=16))
        pixel_data = file.read(width * height)

        # Handle swizzled pixels
        if is_swizzled:
            if bpp == 8:
                pixel_data = swizzle.unswizzle_i8(width, height, pixel_data)
            if bpp == 4:
                pixel_data = swizzle.unswizzle_i4(width, height, pixel_data)

        # Convert 4BPP to 8BPP
        if bpp == 4:
            pixel_data = helpers.convert_to_8bpp(pixel_data)

        # Build converted PNG image
        converted_image = Image.new("P",(width, height))
        converted_image.putdata(pixel_data)
        converted_image.putpalette(rgb_palette)

        # Add transparency/alpha support
        converted_image.convert("RGBA")
        converted_image.info["transparency"] = bytes(alpha_palette)

        # Save the image
        converted_image.save(f'{filename[:-4]}.png', "PNG")


# ---Main function---

# File handling
files_to_convert = filedialog.askopenfilenames(filetypes=[('TDX files', "*.tdx")])

if files_to_convert == "NULL":
    exit()

for filename in files_to_convert:
    convert_texture(filename)