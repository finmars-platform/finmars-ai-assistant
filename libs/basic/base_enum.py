from enum import Enum


class BaseEnum(Enum):
    def __str__(self):
        """Return the string representation of the enum value."""
        return self.value
