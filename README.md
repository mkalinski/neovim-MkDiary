# MkDiary

Very simple plugin for editing diary (or similar) entries, identified by dates.

Inspired by diary function of [vimwiki](https://github.com/vimwiki/vimwiki).

This is a rewrite of my [Vim plugin](github.com/mkalinski/vim-mkdiary) as
a Python plugin, since Vimscript time functions are insufficient for providing
some more convenient arguments. Because the plugin now uses Neovim's remote
plugin interface, it's now a Neovim-only plugin.

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
- `(.|(+|-)<years>|<year>) [.|(+|-)<months>|<month>] [.|(+|-)<days>|<day>]`:
  the main form; the three arguments denote year, month, and day of the entry.
  * `.` means the current year, month, or day.
  * Number preceded by `+` or `-` means the current year, month, or day
    modified by plus/minus given number of units.
  * Natural number to mean that year, month, or day.
  * Modified values don't "roll over", if they sum up to a number too high or
    too low to represent a valid year, month, or day number, that's an error.
  * If days are omitted, the directory for month will be opened.
  * If days and months are omitted, the directory for years will be opened.
- `(+|-)<days>d`: the entry for current day, modified by plus/minus given
  number of days. The `+` or `-` sign, or `d` at the end, are mandatory for
  this form, and no spaces are allowed, to differentiate this form from the
  main one. This forms can cause months or years to "roll over".
- As shortcuts for `. .` and `. . .`, `..` means "current month" and `...`
  means "current day" (essentially the same as calling without arguments).

### Options

- `MkDiary_edit_command`: The command to open and entry in place (like `edit`).
  The command will be passed the absolute path to the entry, which can be an
  existing directory or an existing or not file. It should also handle `!` like
  `edit`.
  * Default: `'edit'`
- `MkDiary_split_command`: The command to open an entry in a split window (like
  `split`). The command will be passed the absolute path to the entry, which
  can be an existing directory or an existing or not file. It should also
  handle `<mods>` like `split`.
  * Default: `'split'`
- `MkDiary_base_dir`: Base directory in which entries will be created. It will
  be crated when a `MkDiary` command is called if it does not exist.
  * Default: `$HOME .. '/Diary'`
- `MkDiary_file_ext`: Extension that is appended to entry file names. Must
  start with a dot. Empty string will disable extension appending.
  * Default: `'.txt'`
