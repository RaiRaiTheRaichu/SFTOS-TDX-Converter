# Unswizzling functions taken from https://github.com/neko68k/rtftool
# Full credit to Neko68k for the algorithms.

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