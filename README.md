# transmission-orphan-smasher / Transmission orphan remover

A python script that can be used to find and remove orphan files. Made to work with [linuxserver's transmission container](https://github.com/linuxserver/docker-transmission/pkgs/container/transmission)

## Usage

Set your transmission parameters to match your setup.

Edit the list called list_of_parent_folders with the list of where torrents would be stored, e.g. labels/download directories. This is because transmission will only return files/folders relative to the torrent itself.

## Known issues
The use of "endswith" for file matching between the OS and transmission may return false positives. Comment out the os.remove in the remove_orphans function to check for these.
