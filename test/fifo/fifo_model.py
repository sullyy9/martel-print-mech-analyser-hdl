from typing import Final

class FifoModel:
    def __init__(self, depth: int) -> None:
        self._data: list[int] = []
        self._depth: Final[int] = depth

    def write(self, word: int) -> None:
        if self.is_full():
            return

        self._data.append(word)

    def read(self) -> int:
        if self.is_empty():
            return 0

        return self._data.pop(0)

    def is_empty(self) -> bool:
        return len(self._data) == 0

    def is_full(self) -> bool:
        return len(self._data) >= (self._depth - 1)

    def count(self) -> int:
        return len(self._data)