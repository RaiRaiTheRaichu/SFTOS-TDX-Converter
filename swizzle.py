# Pixel unswizzling functions taken from https://github.com/neko68k/rtftool
# Full credit to Neko68k for the algorithms.
# Palette unswizzling function taken from https://github.com/bartlomiejduda/ReverseBox
# Full credit to bartlomiejduda for the algorithm.

def unswizzle_i8(w: int, h: int, in_pixels: bytes) -> bytearray:
    out_pixels = bytearray(w * h)

    for y in range(h):
        for x in range(w):
            block_location = (y & (~0xF)) * w + (x & (~0xF)) * 2
            swap_selector = (((y + 2) >> 2) & 0x1) * 4
            pos_y = (((y & (~3)) >> 1) + (y & 1)) & 0x7
            column_location = pos_y * w * 2 + ((x + swap_selector) & 0x7) * 4

            byte_num = ((y >> 1) & 1) + ((x >> 2) & 2)  # 0,1,2,3

            pixel_idx = (y * w) + x
            out_pixels[pixel_idx] = in_pixels[
                block_location + column_location + byte_num
            ]

    return out_pixels

def unswizzle_i4(w: int, h: int, in_bytes: bytes) -> bytearray:
    out_bytes = bytearray((w * h + 1) // 2)

    for y in range(h):
        for x in range(w):
            page_x = x & (~0x7F)
            page_y = y & (~0x7F)

            pages_horz = (w + 127) // 128
            pages_vert = (h + 127) // 128

            page_number = (page_y // 128) * pages_horz + (page_x // 128)

            page32_y = (page_number // pages_vert) * 32
            page32_x = (page_number % pages_vert) * 64

            page_location = page32_y * h * 2 + page32_x * 4

            loc_x = x & 0x7F
            loc_y = y & 0x7F

            block_location = ((loc_x & (~0x1F)) >> 1) * h + (loc_y & (~0xF)) * 2
            swap_selector = (((y + 2) >> 2) & 0x1) * 4
            pos_y = (((y & (~3)) >> 1) + (y & 1)) & 0x7

            column_location = pos_y * h * 2 + ((x + swap_selector) & 0x7) * 4

            byte_num = (x >> 3) & 3

            entry = in_bytes[
                page_location + block_location + column_location + byte_num
            ]
            entry = (entry >> (((y >> 1) & 0x01) * 4)) & 0x0F

            pixel_idx = (y * w) + x
            out_idx = pixel_idx >> 1

            if (pixel_idx & 1) == 0:
                out_bytes[out_idx] = (out_bytes[out_idx] & 0xF0) | entry
            else:
                out_bytes[out_idx] = (entry << 4) | (out_bytes[out_idx] & 0x0F)

    return out_bytes

def unswizzle_palette(palette_data: bytes) -> bytes:
    bytes_per_palette_pixel: int = 4
    converted_palette_data: bytes = b""

    parts: int = int(len(palette_data) / 32)
    stripes: int = 2
    colors: int = 8
    blocks: int = 2
    index: int = 0

    for part in range(parts):
        for block in range(blocks):
            for stripe in range(stripes):
                for color in range(colors):
                    palette_index: int = (
                        index
                        + part * colors * stripes * blocks
                        + block * colors
                        + stripe * stripes * colors
                        + color
                    )
                    palette_offset: int = palette_index * bytes_per_palette_pixel
                    palette_entry = palette_data[palette_offset: palette_offset + bytes_per_palette_pixel]
                    converted_palette_data += palette_entry

    return converted_palette_data