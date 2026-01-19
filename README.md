# Syphon Filter: The Omega Strain TXD Converter

A lightweight python script that converts any texture file (\*.txd) from the PS2 game, Syphon Filter: The Omega Strain, to an easily viewable .png file. All texture types (4bpp, 8bpp, swizzled) are supported.

Currently, there is no way to convert textures back into .txd format, which will likely come in the future if there is sufficient interest and need.

### How to use

*Precompiled Binary Method:*

1. Download the latest `TXD Converter.exe` file from [https://github.com/RaiRaiTheRaichu/SFTOS-TDX-Converter/Releases](https://github.com/RaiRaiTheRaichu/SFTOS-TDX-Converter/releases)
2. Run `TXD Converter.exe` and select your .txd files. Multiple files can be selected at once.

Beware of any false positives caused by an antivirus - python scripts compiled into .exe files tend to trigger AV software. When in doubt, you can always use the manual method below.

*Manual Method:*

1. Install Python 3.10+.
2. Install Pillow for python (by running the python command `pip install Pillow`).
3. Run `main.py` and select your .txd files. Multiple files can be selected at once.

Textures will be converted in the same folder location as the original.

### Options

You can run the program via commandline and use additional options.

--dryrun = Results in no file-saving, but opens the converted image in your default app for PNG files.
--debug = Results in additional debug output, including an `output.log` and `error_list.csv` file generated in the program's directory.
--nofile = Can be used alongside --debug, skips creating/writing text to the `output.log` file.
--folder = Opens a folder selection menu instead of file selection, will recursively scan for texture files.

### Known issues

Some .TXD files still fail to convert or are handled improperly.

Converting back to the .TXD file format is currently not supported.

### Credits

RaiRaiTheRaichu
