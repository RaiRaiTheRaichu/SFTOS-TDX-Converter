def get_palette(color_palette: bytes, mode: str):
    rgb_array = bytearray()
    alpha_array = bytearray()

    if mode == 4:
        palette_size = 16
    else:
        palette_size = 256

    # Color data is stored BGRA
    for color_entry in range(palette_size):
        b = color_palette[color_entry * 4]
        g = color_palette[color_entry * 4 + 1]
        r = color_palette[color_entry * 4 + 2]
        a = color_palette[color_entry * 4 + 3]

        rgb_array.extend([r,g,b])
        alpha_array.append(a)

    # Needed because PNGs require a full color palette, even if unused
    if mode == 4:
        rgb_array.extend([0, 0, 0] * (256 - palette_size))
        alpha_array.extend([255] * (256 - palette_size))

    return rgb_array, alpha_array

def convert_to_8bpp(pixel_data: bytes):
    converted_8bpp = bytearray()
    for pixel in pixel_data:
        first_pixel = (pixel >> 4) & 0x0F
        second_pixel = pixel & 0x0F
        converted_8bpp.append(second_pixel)
        converted_8bpp.append(first_pixel)
    return converted_8bpp