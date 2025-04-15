from dataclasses import asdict
from typing import List, Tuple

from ada.user.messages import SystemMessage

_DEFAULT_DELAY = 0.005
_INVOLVED_DELAY = 0.05
_CONSIDERATE_DELAY = 0.07


class StyleChunker:
    def __init__(self, style: str = "default") -> None:
        self.style = style
        self.texts = []

    def set_style(self, style: str) -> None:
        self.style = style

    def add_message(self, message: str) -> None:
        self.texts.append(message)

    def get_delay_divisor(self) -> float:
        text_length = sum(len(text) for text in self.texts)
        divisor = min(max(1, text_length / 100), 10)
        return divisor

    def get_chunked_messages(
        self,
    ) -> List[Tuple[SystemMessage, float]]:
        chunks = []
        divisor = self.get_delay_divisor()

        if not self.texts:
            return chunks

        if self.style == "considerate":
            chunks.append(
                (asdict(SystemMessage("", info="NEW")), _DEFAULT_DELAY)
            )
        for text in self.texts:
            if self.style == "default":
                chunks.append(
                    (asdict(SystemMessage("", info="NEW")), _DEFAULT_DELAY)
                )
                chunks.append(
                    (asdict(SystemMessage(text=text)), _DEFAULT_DELAY)
                )
            elif self.style == "involved":
                chunks.append(
                    (asdict(SystemMessage("", info="NEW")), _DEFAULT_DELAY)
                )
                for word in text.split():
                    chunks.append(
                        (
                            asdict(SystemMessage(text=f"{word} ")),
                            _INVOLVED_DELAY / divisor,
                        )
                    )
            elif self.style == "considerate":
                for letter in text:
                    chunks.append(
                        (
                            asdict(SystemMessage(text=letter)),
                            _CONSIDERATE_DELAY / divisor,
                        )
                    )
                chunks.append(
                    (asdict(SystemMessage(" ")), _DEFAULT_DELAY / divisor)
                )
            else:
                raise ValueError(f"Style {self.style} not supported")

        self.texts = []
        return chunks
