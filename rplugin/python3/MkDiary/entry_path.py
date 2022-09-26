# Copyright 2022 Michał Kaliński

__all__ = [
    "EntryPathInfo",
    "EntryPathParser",
    "InvalidArgsError",
    "InvalidEntryDateError",
]

import dataclasses
import datetime
import re
from collections.abc import Callable
from functools import cached_property
from pathlib import Path


@dataclasses.dataclass(frozen=True)
class EntryPathInfo:
    path: Path
    is_dir: bool


class EntryPathParser:
    _PATTERN_SIGNED_NUM = re.compile(r"[-+]\d+")
    _PATTERN_SIGNED_NUM_DAYS = re.compile(r"([-+]\d+)d")

    @cached_property
    def _today(self) -> datetime.date:
        return datetime.date.today()

    def parse_from_args(self, argstr: str) -> EntryPathInfo:
        args = argstr.split()
        argc = len(args)

        if argc == 0:
            return EntryPathInfo(self._get_entry_path(self._today), False)

        if argc == 1:
            return self._parse_1_arg(args[0])

        if argc == 2:
            return self._parse_2_args(*args)

        if argc == 3:
            return self._parse_3_args(*args)

        raise InvalidArgsError(args)

    @staticmethod
    def _get_year_dir_path(date: datetime.date) -> Path:
        return Path(str(date.year))

    @staticmethod
    def _get_month_dir_path(date: datetime.date) -> Path:
        return Path(str(date.year), str(date.month).rjust(2, "0"))

    @staticmethod
    def _get_entry_path(date: datetime.date) -> Path:
        return Path(
            str(date.year),
            str(date.month).rjust(2, "0"),
            str(date.day).rjust(2, "0"),
        )

    @staticmethod
    def _make_date(year: int, month: int = 1, day: int = 1) -> datetime.date:
        try:
            return datetime.date(year, month, day)
        except ValueError:
            raise InvalidEntryDateError(year, month, day)

    def _get_today_year(self) -> int:
        return self._today.year

    def _get_today_month(self) -> int:
        return self._today.month

    def _get_today_day(self) -> int:
        return self._today.day

    @classmethod
    def _parse_relative_num(cls, value: str) -> int | None:
        matched_relative_num = cls._PATTERN_SIGNED_NUM.fullmatch(value)

        return int(matched_relative_num[0]) if matched_relative_num else None

    @staticmethod
    def _parse_absolute_num(value: str) -> int | None:
        return int(value) if value.isdigit() else None

    @classmethod
    def _parse_regular_arg(
        cls, arg: str, today_getter: Callable[[], int]
    ) -> int | None:
        if arg == ".":
            return today_getter()

        if relative_value := cls._parse_relative_num(arg):
            return today_getter() + relative_value

        if absolute_value := cls._parse_absolute_num(arg):
            return absolute_value

        return None

    def _parse_1_arg(self, arg: str) -> EntryPathInfo:
        if parsed_dots := self._parse_arg_1_many_dots(arg):
            return parsed_dots

        if parsed_relative_days := self._parse_arg_1_relative_days(arg):
            return parsed_relative_days

        if year_value := self._parse_regular_arg(arg, self._get_today_year):
            return EntryPathInfo(
                self._get_year_dir_path(self._make_date(year_value)), True
            )

        raise InvalidArgsError(arg)

    def _parse_arg_1_many_dots(self, arg: str) -> EntryPathInfo | None:
        if arg == ".":
            return EntryPathInfo(self._get_year_dir_path(self._today), True)

        if arg == "..":
            return EntryPathInfo(self._get_month_dir_path(self._today), True)

        if arg == "...":
            return EntryPathInfo(self._get_entry_path(self._today), False)

        return None

    def _parse_arg_1_relative_days(self, arg: str) -> EntryPathInfo | None:
        if matched_relative_days := self._PATTERN_SIGNED_NUM_DAYS.fullmatch(
            arg
        ):
            return EntryPathInfo(
                self._get_entry_path(
                    self._today
                    + datetime.timedelta(days=int(matched_relative_days[1]))
                ),
                False,
            )

        return None

    def _parse_2_args(self, year_arg: str, month_arg: str) -> EntryPathInfo:
        if (
            year_value := self._parse_regular_arg(
                year_arg, self._get_today_year
            )
        ) is None:
            raise InvalidArgsError(year_arg)

        if (
            month_value := self._parse_regular_arg(
                month_arg, self._get_today_month
            )
        ) is None:
            raise InvalidArgsError(year_arg, month_arg)

        return EntryPathInfo(
            self._get_month_dir_path(self._make_date(year_value, month_value)),
            True,
        )

    def _parse_3_args(
        self, year_arg: str, month_arg: str, day_arg: str
    ) -> EntryPathInfo:
        if (
            year_value := self._parse_regular_arg(
                year_arg, self._get_today_year
            )
        ) is None:
            raise InvalidArgsError(year_arg)

        if (
            month_value := self._parse_regular_arg(
                month_arg, self._get_today_month
            )
        ) is None:
            raise InvalidArgsError(year_arg, month_arg)

        if (
            day_value := self._parse_regular_arg(day_arg, self._get_today_day)
        ) is None:
            raise InvalidArgsError(year_arg, month_arg, day_arg)

        return EntryPathInfo(
            self._get_entry_path(
                self._make_date(year_value, month_value, day_value)
            ),
            False,
        )


class InvalidEntryDateError(Exception):
    pass


class InvalidArgsError(Exception):
    pass
