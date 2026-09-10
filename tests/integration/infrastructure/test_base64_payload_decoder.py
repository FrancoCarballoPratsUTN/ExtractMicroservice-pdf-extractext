"""Integration tests for the Base64 payload decoder adapter."""

import base64

import pytest

from app.domain.exceptions import InvalidBase64Error
from app.domain.ports.payload_decoder import PayloadDecoder
from app.infrastructure.encoding.base64_payload_decoder import Base64PayloadDecoder


class TestBase64PayloadDecoder:
    def test_implements_the_payload_decoder_port(self):
        assert isinstance(Base64PayloadDecoder(), PayloadDecoder)

    def test_decodes_standard_base64_to_original_bytes(self):
        decoder = Base64PayloadDecoder()
        expected = b"raw pdf bytes"

        assert decoder.decode(base64.b64encode(expected).decode("ascii")) == expected

    def test_roundtrips_arbitrary_binary_bytes(self):
        decoder = Base64PayloadDecoder()
        expected = bytes(range(256)) * 4

        assert decoder.decode(base64.b64encode(expected).decode("ascii")) == expected

    def test_rejects_urlsafe_base64(self):
        decoder = Base64PayloadDecoder()

        with pytest.raises(InvalidBase64Error):
            decoder.decode("8j-_kA0=")

    def test_rejects_payload_containing_whitespace(self):
        decoder = Base64PayloadDecoder()
        encoded = base64.b64encode(b"data").decode("ascii")
        payload = encoded[:4] + " \n " + encoded[4:]

        with pytest.raises(InvalidBase64Error):
            decoder.decode(payload)

    def test_rejects_non_base64_characters(self):
        decoder = Base64PayloadDecoder()

        with pytest.raises(InvalidBase64Error):
            decoder.decode("%%%not-base64%%%")

    def test_rejects_incorrect_padding(self):
        decoder = Base64PayloadDecoder()
        truncated = base64.b64encode(b"data").decode("ascii")[:-1]

        with pytest.raises(InvalidBase64Error):
            decoder.decode(truncated)
