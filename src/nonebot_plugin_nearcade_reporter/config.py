import re

from pydantic import (
    BaseModel,
    field_validator,
    model_validator,
)
from typing_extensions import Self

from nonebot_plugin_nearcade_reporter.errors import (
    InvalidArcadeSourceError,
    InvalidRegexError,
    MissingRegexGroupError,
)

from pydantic import PrivateAttr


class QueryAttendanceRegexConfig(BaseModel):
    enabled: bool = True
    pattern: str = r"^(?P<arcade>\S+)几人$"
    arcade_alias: str = "arcade"
    reply_message: str = "{arcade} 当前人数: {count}"

    @staticmethod
    def _extract_group_names(pattern: str) -> set[str]:
        try:
            regex = re.compile(pattern)
        except re.error as e:
            raise InvalidRegexError(str(e)) from e

        return set(regex.groupindex.keys())

    @model_validator(mode="after")
    def validate_group_names(self) -> Self:
        groups = self._extract_group_names(self.pattern)

        if self.arcade_alias not in groups:
            raise MissingRegexGroupError(self.arcade_alias, groups)

        return self


class UpdateAttendanceRegexConfig(BaseModel):
    enabled: bool = True
    pattern: str = r"^机厅人数\s*(?P<arcade>\S+)\s*(?P<count>(?:100|[1-9]\d?|0))$"
    arcade_group_name: str = "arcade"
    count_group_name: str = "count"
    reply_message: str = "更新成功，{arcade} 当前人数: {count}"

    @staticmethod
    def _extract_group_names(pattern: str) -> set[str]:
        try:
            regex = re.compile(pattern)
        except re.error as e:
            raise InvalidRegexError(str(e)) from e

        return set(regex.groupindex.keys())

    @model_validator(mode="after")
    def validate_group_names(self) -> Self:
        groups = self._extract_group_names(self.pattern)

        if self.arcade_group_name not in groups:
            raise MissingRegexGroupError(self.arcade_group_name, groups)

        if self.count_group_name not in groups:
            raise MissingRegexGroupError(self.count_group_name, groups)
        return self


class ArcadeConfig(BaseModel):
    arcade_source: str
    aliases: set[str]
    default_game_id: int

    @field_validator("arcade_source")
    @classmethod
    def validate_source_availability(cls, value: str) -> str:
        if value not in {"bemani", "ziv"}:
            raise InvalidArcadeSourceError(value)
        return value


class Config(BaseModel):
    api_token: str = ""
    query_attendance_match: QueryAttendanceRegexConfig = QueryAttendanceRegexConfig()
    update_attendance_match: UpdateAttendanceRegexConfig = UpdateAttendanceRegexConfig()
    arcades: dict[int, ArcadeConfig] = {}

    _alias_index: dict[str, int] = PrivateAttr(default_factory=dict)

    @model_validator(mode="after")
    def build_alias_index(self) -> Self:
        index: dict[str, int] = {}

        for arcade_id, arcade in self.arcades.items():
            for alias in arcade.aliases:
                key = alias.casefold()
                index[key] = arcade_id

        self._alias_index = index
        return self

    def find_arcade_by_alias(self, arcade_name: str) -> tuple[int, ArcadeConfig]:
        key = arcade_name.casefold()

        arcade_id = self._alias_index.get(key)
        if arcade_id is None:
            return [-1, None]

        return arcade_id, self.arcades[arcade_id]
