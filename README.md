# xtool

Provide a set of tools to manage local XWiki installations

## Requirements

### On Debian

* `python3`
* `python3-virtualenv`
* `virtualenv`

## Installation

1. Clone the project in `~/.xtool` : `git clone https://github.com/aubincleme/xtool.git ~/.xtool`
1. To access and use XTool, two options are possible:
   * Add `export PATH="$HOME/.xtool:$PATH"` to your `.*rc`
   * Create a symlink from the main XTool executable `~/.xtool/x` in a `~/.local/bin`: `ln -s ~/.xtool/x ~/.local/bin`. Note that you need to have `~/.local/bin` in your `$PATH` for this method to work.
1. Set up XTool virtual environment : 
   * `cd ~/.xtool/xtool && virtualenv -p $(which python3) venv`
   * `source venv/bin/activate`
   * `pip install -r xtool/requirements.txt`

## Upgrade

1. Update the source code of the project : `cd ~/.xtool && git pull`
1. Update the pip dependencies :
   * `cd ~/.xtool/xtool && source venv/bin/activate`
   * `pip install -U requirements.txt`

## General documentation

### Linking and unlinking instance storage

XTool comes with a feature that allows to symlink the contents of each WEB-INF/lib folder in an instance to the equivalent contents of the version corresponding to the instance.

This feature is **disabled by default**, because it could not work for some old XWiki installations (so far, I've not checked since when the jetty-hsqldb distribution supports symlinks in its WEB-INF/lib ; it seems to be before XWiki 8).
Here is a small cheatsheet on the commands that you can use to symlink or unsymlink an instance :

```
# Migrate instance-name to use linked instance storage
x instance symlink -i instance-name
# Migrate all instances to use linked instance storage
x instance symlink --all
# Undo linked instance storage for a given instance
x instance symlink -i instance-name --undo
# Show if xtool will attempt to automatically link an instance when creating it
x config linkInstanceStorage
# Enable automatic linking of instance storage when creating a new instance
x config --set True linkInstanceStorage
# Disable automatic linking of instance storage when creating a new instance
x config --set False linkInstanceStorage
```
