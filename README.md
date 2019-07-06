# xtool

Provide a set of tools to manage local XWiki installations

## Requirements

### On Debian

* `python3`
* `virtualenv`

## Installation

1. Clone the project in `~/.xtool` : `git clone https://github.com/aubincleme/xtool.git ~/.xtool`
1. Add `export PATH="$HOME/.xtool/xtool:$PATH"` to your `.*rc` to access XTool
1. Set up XTool virtual environment : 
  * `cd ~/.xtool/xtool && virtualenv $(which python3) venv`
  * `source venv/bin/activate`
  * `pip install -r requirements.txt`

## Upgrade

1. Update the source code of the project : `cd ~/.xtool && git pull`
1. Update the pip dependencies :
  * `cd ~/.xtool/xtool && source venv/bin/activate`
  * `pip install -U requirements.txt`
