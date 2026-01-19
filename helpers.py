import math
import sys
import os

def get_save_option() -> bool:
    return not '--dryrun' in sys.argv

def get_folder_mode() -> bool:
    return '--folder' in sys.argv

def get_palette(color_palette: bytes, mode: int) -> tuple[bytearray, bytearray]:
    rgb_array = bytearray()
    alpha_array = bytearray()

    if mode == 4:
        palette_size = 16
    else:
        palette_size = 256

    # Color data is stored RGBA, little endian
    for color_entry in range(palette_size):
        r = color_palette[color_entry * 4]
        g = color_palette[color_entry * 4 + 1]
        b = color_palette[color_entry * 4 + 2]
        a = color_palette[color_entry * 4 + 3]

        rgb_array.extend([r,g,b])
        alpha_array.append(a)

    # Needed because PNGs require a full color palette, even if unused
    if mode == 4:
        rgb_array.extend([0, 0, 0] * (256 - palette_size))
        alpha_array.extend([255] * (256 - palette_size))

    return rgb_array, alpha_array

def convert_to_8bpp(pixel_data: bytes) -> bytearray:
    converted_8bpp = bytearray()
    for pixel in pixel_data:
        first_pixel = (pixel >> 4) & 0x0F
        second_pixel = pixel & 0x0F
        converted_8bpp.append(second_pixel)
        converted_8bpp.append(first_pixel)
    return converted_8bpp

def pad_bytes(bytes_in: bytes, pad_length: int) -> bytes:
    array = bytearray(bytes_in)
    array.extend(b'x\0' * math.floor(pad_length/2))
    return array

def scan_folders(folder_path: str) -> list[str]:
    file_list = []

    for root, dirs, files in os.walk(folder_path):
        for file in files:
            if file.lower().endswith(".tdx"):
                full_path = os.path.join(root, file)
                file_list.append(full_path)

    return file_list