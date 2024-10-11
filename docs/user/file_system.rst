.. _file_system:

File System
===========

The `file_system` parameter is used during the download process to specify the type of file system where the file will be stored. This is useful to guarantee compatibility with different operating systems, this parameter removes characters from the name of the file to be downloaded, this guarantees the download even if there are characters not allowed by the file system.


Currently supported file systems are:

- **Linux**: `ext4`, `ext3`, `ext2`, `Btrfs`, `XFS`, `ZFS`
- **Windows**: `NTFS`, `FAT32`, `exFAT`, `ReFS`
- **macOS**: `APFS`, `HFS+`
- **BSD/Unix**: `UFS`

When passing the `file_system` parameter, the system will check if the specified file system is available. If it is not compatible, an exception will be raised.

**Usage Example**::
        >>> ys.download(file_system='exFAT')

**If you don't know the type of file system, you can pass it generically, for example, the name of the operating system**::
        >>> ys.download(file_system='Linux')

**macOS**::
        >>> ys.download(file_system='APFS')

**If you are using Linux it is recommended to use a format for the Linux file system for example ext4, this will allow more characters for example ':', '*', '?', '"', '<', '>', '|'**::
        >>> ys.download(file_system='ext4')

If `file_system` is not specified, pytubefix's default file system will be the NTFS that is used in Windows, this does not interfere in any way with the functioning of the library, it will only remove characters that cause problems in the operating system's file system.
