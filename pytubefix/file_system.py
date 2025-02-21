
windows = ['Windows', 'NTFS', 'FAT32', 'exFAT', 'ReFS']
linux = ['Linux', 'ext2', 'ext3', 'ext4', 'Btrfs', 'XFS', 'ZFS']
macOS = ['macOS', 'APFS', 'HFS+']
bsd_unix = ['BSD', 'UFS']
network_filesystems = ['CIFS', 'SMB']


windows_translation = str.maketrans({
            '\\': '',
            '/': '',
            '?': '',
            ':': '',
            '*': '',
            '"': '',
            '<': '',
            '>': '',
            '|': '',
        })

linux_translation = str.maketrans({
            '/': '',
        })

macos_translation = str.maketrans({
            '/': '',
        })

bsd_translation = str.maketrans({
            '/': '',
        })

network_filesystems_translation = str.maketrans({
            '\\': '',
            '/': '',
            '?': '',
            ':': '',
            '*': '',
            '"': '',
            '<': '',
            '>': '',
            '|': '',
        })

def file_system_verify(file_type) -> dict:
    """
    Returns a translation table to remove invalid characters for a specified file system type.

    This function identifies the file system type and returns a translation table for removing 
    characters that are not allowed in filenames for that specific file system.

    Args:
        file_type (str): The type of file system being checked. Supported file systems include:
                         - Windows: NTFS, FAT32, exFAT, ReFS
                         - Linux: ext2, ext3, ext4, Btrfs, XFS, ZFS
                         - macOS: APFS, HFS+
                         - BSD/UNIX: UFS
                         - Network Filesystems: CIFS, SMB

    Returns:
        dict: A translation table where invalid characters are mapped to an empty string.

    Example:
        >>> ys = yt.streams.get_highest_resolution()
        >>> ys.download(file_system='ext4')

    Raises:
        None, but prints a message if the file system type is not recognized.
    """

    if file_type in windows:
        return windows_translation
    elif file_type in linux:
        return linux_translation
    elif file_type in macOS:
        return macos_translation
    elif file_type in bsd_unix:
        return bsd_translation
    elif file_type in network_filesystems:
        return network_filesystems_translation
