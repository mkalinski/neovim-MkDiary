# MkDiary

Very simple plugin for editing diary (or similar) entries, identified by dates.

Inspired by diary function of [vimwiki](https://github.com/vimwiki/vimwiki).

This is a rewrite of my [Vim plugin](github.com/mkalinski/vim-mkdiary) as
a Python plugin, since Vimscript time functions are insufficient for providing
some more convenient arguments. ~~Because the plugin now uses Neovim's remote
plugin interface, it's now a Neovim-only plugin.~~ It no longer uses Neovim's
remote plugin interface, in anticipation of it being completely overhauled;
it now uses the legacy interface,
with as little functionality in Python as possible,
so it should actually work on Vim now too.

## What the plugin does

It provides commands to create and edit files within a directory structure
organized by dates:

```
<base_directory>
├── 2022
│   ├── 01
│   │   ├── 01.txt
│   │   ├── 02.txt
│   │   ├── 03.txt
│   │   ...
│   ├── 02
│   │   ├── 01.txt
│   │   ├── 02.txt
│   │   ├── 03.txt
...
```

Year and month directories are automatically created when they're accessed
with the `MkDiary` commands.

## Usage

### Commands

- `MkDiary[!] <args>`: Edits a diary entry, denoted by `<args>`, in
  the current window; like `edit`, also accepting `!` in the same way.
- `<mods> MkDiarySplit[!] <args>`: Edits a diary entry, denoted by `<args>`, in
  a split window; like `split`, also accepting `<mods>` (`vertical`, etc.) in
  the same way.

#### Args

Both `MkDiary` commands accept the same arguments. There are several accepted
forms, each of them denoting a certain entry or directory date.

- **No arguments**: the entry for current date.
- `(.|<year>) [.|<month>] [.|<day>]`:
  the main form; the three arguments denote year, month, and day of the entry.
  * `.` means the current year, month, or day.
  * Natural number to mean that year, month, or day.
  * If days are omitted, the directory for month will be opened.
  * If days and months are omitted, the directory for years will be opened.
- `(+|-)<days>`: the entry for current day, modified by plus/minus given
  number of days. The `+` or `-` sign is mandatory for
  this form.

### Options

- `MkDiary_base_dir`: Base directory in which entries will be created. It will
  be crated when a `MkDiary` command is called if it does not exist.
  * Default: `$HOME .. '/Diary'`
- `MkDiary_file_ext`: Extension that is appended to entry file names. Must
  start with a dot. Empty string will disable extension appending.
  * Default: `'.txt'`
