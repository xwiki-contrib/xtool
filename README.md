# xtool

Provide a set of tools to manage local XWiki installations

## Requirements

### On Debian

* `python3`
* `python3-virtualenv`

## Installation

1. Clone the project in `~/.xtool` : `git clone https://github.com/aubincleme/xtool.git ~/.xtool`
1. To access and use XTool, two options are possible:
   * Add `export PATH="$HOME/.xtool:$PATH"` to your `.*rc`
   * Create a symlink from the main XTool executable `~/.xtool/x` in a `~/.local/bin`: `ln -s ~/.xtool/x ~/.local/bin`
1. Set up XTool virtual environment : 
   * `cd ~/.xtool/xtool && virtualenv $(which python3) venv`
   * `source venv/bin/activate`
   * `pip install -r requirements.txt`

## Upgrade

1. Update the source code of the project : `cd ~/.xtool && git pull`
1. Update the pip dependencies :
   * `cd ~/.xtool/xtool && source venv/bin/activate`
   * `pip install -U requirements.txt`
