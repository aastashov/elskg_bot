"""Models."""
from dataclasses import dataclass

default_status_text = "Добавлен в бота"


@dataclass
class Package:
    """Model of Package."""

    chat_id: int
    tracking: str
    status_text: str = default_status_text
    notified: bool = False

    def as_tuple(self) -> tuple:
        return self.chat_id, self.tracking, self.status_text, self.notified

    @classmethod
    def from_row(cls, *args):
        return cls(chat_id=args[0], tracking=args[1], status_text=args[2], notified=args[3])

    @property
    def status_text_is_default(self) -> bool:
        return self.status_text == default_status_text
