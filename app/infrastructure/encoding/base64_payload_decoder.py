"""Standard Base64 adapter implementing the PayloadDecoder port."""

import base64
from binascii import Error as BinasciiError

from app.domain.exceptions import InvalidBase64Error
from app.domain.ports.payload_decoder import PayloadDecoder


class Base64PayloadDecoder(PayloadDecoder):
    """Strictly decode a standard Base64 string into raw bytes in memory."""

    def decode(self, payload: str) -> bytes:
        try:
            return base64.b64decode(payload, validate=True)
        except (BinasciiError, ValueError) as exc:
            raise InvalidBase64Error(
                "The provided payload is not valid standard Base64."
            ) from exc
