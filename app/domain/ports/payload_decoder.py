"""Abstract port for decoding string payloads into raw bytes."""

from abc import ABC, abstractmethod


class PayloadDecoder(ABC):
    """Boundary that infrastructure adapters implement with an encoding library."""

    @abstractmethod
    def decode(self, payload: str) -> bytes:
        """Decode a string payload into raw bytes.

        Raises:
            InvalidBase64Error: If the payload is not valid Base64.
        """
