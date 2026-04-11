# MkDiary

Very simple plugin for editing diary (or similar) entries, identified by dates.

Inspired by diary function of [vimwiki](https://github.com/vimwiki/vimwiki).

This is a rewrite of my [Vim plugin](github.com/mkalinski/vim-mkdiary) as
a Lua plugin, for convenience.

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

The base, year, and month directories are automatically created
when they're first accessed with the `MkDiary` commands.

## Setup

The `setup()` function needs to be called to setup the plugin's commands.
It optionally takes a table with the following options:

- `base_dir`: The base directory where diary entries are put into.
- `file_ext`: File extension for diary entry files.

The following example show the default values for the options:

```lua
require'mkdiary'.setup{
    base_dir = vim.fs.normalize'~/Diary',
    file_ext = '.txt'
}
```

## Usage

### Commands

- `MkDiary[!] <args>`: Edits a diary entry, denoted by `<args>`, in
  the current window; like `edit`, also accepting `!` in the same way.
- `<mods> MkDiarySplit[!] <args>`: Edits a diary entry, denoted by `<args>`,
  in a split window; like `split`, also accepting `<mods>` (`vertical`, etc.)
  in the same way.

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
