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

    @pynvim.function("MkDiary_open", sync=True)
    def open(self, args: list[Any]) -> None:
        try:
            self._inner_open(args)
        except _VimMessageError as err:
            self._vim.api.err_writeln(str(err))

    def _inner_open(self, args: list[Any]) -> None:
        try:
            open_command, entry_args = args
            open_command = str(open_command)
            entry_args = str(entry_args)
        except ValueError:
            raise _VimMessageError(
                "Excepted 2 str arguments (open_command, entry_args); got: "
                + repr(args)
            )

        entry_path_info = self._parse_args(entry_args)
        diary_base_dir = self._get_base_dir()
        entry_full_path = diary_base_dir / entry_path_info.path

        if entry_path_info.is_dir:
            self._prepare_dir_path(entry_full_path)
        else:
            entry_full_path = self._prepare_entry_path(entry_full_path)

        self._vim.command(
            f"execute {open_command!r} fnameescape({str(entry_full_path)!r})"
        )
        self._vim.command(
            f"execute 'lcd' fnameescape({str(diary_base_dir)!r})"
        )

    def _parse_args(self, args: str) -> EntryPathInfo:
        try:
            return EntryPathParser().parse_from_args(args)
        except InvalidArgsError as err:
            raise _VimMessageError(f"Invalid command args: {err.args}")
        except InvalidEntryDateError as err:
            raise _VimMessageError(f"Invalid date: {err.args}")

    @staticmethod
    def _prepare_dir_path(path: Path) -> None:
        path.mkdir(parents=True, exist_ok=True)

    def _prepare_entry_path(self, path: Path) -> Path:
        path.parent.mkdir(parents=True, exist_ok=True)

        entry_ext = self._get_file_ext()

        try:
            return path.with_suffix(entry_ext)
        except ValueError:
            raise _VimMessageError(
                f"Invalid file extension (must start with a dot): {entry_ext}"
            )

    def _get_base_dir(self) -> Path:
        return Path(
            self._vim.vars.get("MkDiary_base_dir")
            or os.path.expanduser("~/Diary")
        )

    def _get_file_ext(self) -> str:
        return self._vim.vars.get("MkDiary_file_ext", ".txt")


class _VimMessageError(Exception):
    def __init__(self, message: str) -> None:
        super().__init__(message)
        self.message = message

    def __str__(self) -> str:
        return self.message
