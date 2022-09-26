# Copyright 2022 Michał Kaliński

__all__ = ["MkDiaryPlugin"]

import os
from pathlib import Path
from typing import Any

import pynvim

from .entry_path import (
    EntryPathInfo,
    EntryPathParser,
    InvalidArgsError,
    InvalidEntryDateError,
)


@pynvim.plugin
class MkDiaryPlugin:
    def __init__(self, vim):
        self._vim = vim
        self._opts = _Options(vim)

    @pynvim.function("MkDiary_open", sync=True)
    def open(self, args: list[Any]) -> None:
        try:
            open_command, entry_args = args
            open_command = str(open_command)
            entry_args = str(entry_args)
        except ValueError:
            self._vim.api.err_writeln(
                "Excepted 2 str arguments (open_command, entry_args); got: "
                + repr(args)
            )
            return

        if (entry_path_info := self._parse_args(entry_args)) is None:
            return

        diary_base_dir = self._opts.get_base_dir()
        entry_full_path = diary_base_dir / entry_path_info.path

        if entry_path_info.is_dir:
            self._prepare_dir_path(entry_full_path)
        elif (
            entry_full_path := self._prepare_entry_path(entry_full_path)
        ) is None:
            return

        self._vim.command(
            f"execute {open_command!r} fnameescape({str(entry_full_path)!r})"
        )
        self._vim.command(
            f"execute 'lcd' fnameescape({str(diary_base_dir)!r})"
        )

    def _parse_args(self, args: str) -> EntryPathInfo | None:
        try:
            return EntryPathParser().parse_from_args(args)
        except InvalidArgsError as err:
            self._vim.api.err_writeln(f"Invalid command args: {err.args}")
        except InvalidEntryDateError as err:
            self._vim.api.err_writeln(f"Invalid date: {err.args}")

        return None

    @staticmethod
    def _prepare_dir_path(path: Path) -> None:
        path.mkdir(parents=True, exist_ok=True)

    def _prepare_entry_path(self, path: Path) -> Path | None:
        path.parent.mkdir(parents=True, exist_ok=True)

        entry_ext = self._opts.get_file_ext()

        try:
            return path.with_suffix(entry_ext)
        except ValueError:
            self._vim.api.err_writeln(
                f"Invalid file extension (must start with a dot): {entry_ext}"
            )

        return None


class _Options:
    def __init__(self, vim):
        self._vim = vim

    def get_base_dir(self) -> Path:
        return Path(
            self._vim.vars.get("MkDiary_base_dir")
            or os.path.expanduser("~/Diary")
        )

    def get_file_ext(self) -> str:
        return self._vim.vars.get("MkDiary_file_ext", ".txt")
