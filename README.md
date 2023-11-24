# LIBRER
A file cataloging program with extensive customization options to suit user preferences.

**The software and this document are under development and in a pre-release state.**

## Features:
The primary purpose of this software is to enable users to catalog their files, particularly on removable media like memory cards and portable drives. It allows user to add metadata, referred to here as **custom data**, and facilitates future searching through the created records. **Custom data** consists of textual information acquired through the execution of user-chosen commands or scripts. **Custom data** may include any text data customized to meet the user's requirements, restricted only by the available memory and the software accessible for data retrieval. The retrieved data is stored in a newly created database record and can be utilized for search or verification purposes.

## Screenshots:

#### New record creation dialog:
![image info](./info/new_record.png)

#### Search dialog:
![image info](./info/search.png)

## Download:
The portable executable for **Linux** and **Windows** can be downloaded from the Releases site:

https://github.com/PJDude/librer/releases

main distributions:

**librer.**{version}**.portable.linux.tgz**
**librer.**{version}**.portable.windows.zip**
contain portable executables with necessary libraries made by [PyInstaller](https://pyinstaller.org/en/stable). Files with **.onefile** postfix contain self-extracting single-file distributions. They are more handy but start a little slower than main distributions (need of unpacking to temporary folder). Onefile distribution also may cause more false positive anti virus alerts (see below).

**auxiliary** distributions contain compiled executable binaries made by [Nuitka](https://github.com/Nuitka/Nuitka).

## Guidelines for crafting custom data extractors
Custom data extractor is a command that can be invoked with a single parameter - the full path to a specific file from which data is extracted. The command should provide the expected data in any textual format to the standard output (stdout). CDE can be an executable file (e.g., 7z, zip, ffmpeg, md5sum etc.) or an executable shell script (extract.sh, extract.bat etc.). The conditions it should meet are reasonably short execution time and reasonably limited information output. The criteria allowing the execution of a particular Custom data extractor include the file extension and the file size range.

## Examples of Custom data extractor


> "7z l" - Listing the contents of the archive. Applicable to files like *.7z, *.zip, etc. (linux)

> "C:\Program Files\\[7-Zip](https://www.7-zip.org)\7z.exe l"  - Listing the contents of the archive (windows)

> "cat" - Listing the contents of the entire file. May be applied to *.cue files or media playlists *.m3u or any text files (Linux)

> "cmd /c more"  - Listing the contents of the entire file. May be applied to *.cue files or media playlists *.m3u or any text files (windows)

> "[ffprobe](https://ffmpeg.org/ffprobe.html) -hide_banner" - get media tags and other metadata from media files like *.mp3 etc.

> "[exiftool](https://exiftool.sourceforge.net/)" get exif data from images like *.jpg and many more

> "[pdftotext](https://linux.die.net/man/1/pdftotext) - - <" - get text content of pdf file

> "strings" - get printable strings from any file

> "anything.sh/anything.bat"  - maybe not exactly "anything", but use your own script to apply more complex criteria to individual files and process the data to be stored.

## Usage tips:
- don't put any destructive actions in your Custom Data Extractors scrips
- try to keep as little custom data as possible, to speed up scanning and searching records and keep record files small
- if general purpose and generally available tools produce too much and not needed text data, write a wrapper script (*.sh, *bat) executing specific tool and post-process retrieved data. Wrapper can also help when the tool expects more variable parameters or in an unusual order
- You don't have to use Custom Data if you don't need to. Only the file system will be cataloged.

## Supported platforms:
- Linux
- Windows (10,11)

## Portability
**librer** writes log files, configuration and database files in runtime. Default location for these files is **logs**, **db** subfolders and folder of **librer** executable . If there are no write access rights to such folder, platform-specific folders are used for cache, settings and logs (provided by **appdirs** module). You can use --appdirs command line switch to force that behavior even when local folders are accessible.


## Technical information
Record in librer is the result of a single scan operation and is shown as one of many top nodes in the main tree window. Contains a directory tree with collected custom data and CRC data. It is stored as a single .dat file in librer database directory. Its internal format is optimized for security, fast initial access and maximum compression (just check :)) Every section is a python data structure serialized by [pickle](https://docs.python.org/3/library/pickle.html) and compressed separately by [Zstandard](https://pypi.org/project/zstandard/) algorithm. The record file, once saved, is never modified afterward. It can only be deleted upon request or exported. All record files are independent of each other.

###### Manual build (linux):
```
pip install -r requirements.txt
./scripts/icons.convert.sh
./scripts/version.gen.sh
./scripts/pyinstaller.run.sh
```
###### Manual build (windows):
```
pip install -r requirements.txt
.\scripts\icons.convert.bat
.\scripts\version.gen.bat
.\scripts\pyinstaller.run.bat
```
###### Manual running of python script:
```
pip install -r requirements.txt
./scripts/icons.convert.sh
./scripts/version.gen.sh

python3 ./src/librer.py
```

## Licensing
- **librer** is licensed under **[MIT license](./LICENSE)**
