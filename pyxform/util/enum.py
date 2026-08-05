from enum import StrEnum as StrEnumBase


class StrEnum(StrEnumBase):
    """Base Enum class with common helper function."""

    @classmethod
    def value_list(cls) -> list:
        return list(cls.__members__.values())

    @classmethod
    def value_set(cls) -> set:
        return set(cls.__members__.values())

    @classmethod
    def value_str_sorted(cls) -> str:
        return ", ".join(sorted(cls.__members__.values()))
