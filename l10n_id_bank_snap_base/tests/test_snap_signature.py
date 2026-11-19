# Copyright 2026 PT Solusi Aglis Indonesia. (http://solusiaglis.co.id)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
import base64
import hashlib
import hmac
from datetime import datetime

from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding

from .common import TEST_PUBLIC_KEY, SnapCommon

BODY = b'{"partnerReferenceNo":"1","accountNo":"1234567890"}'
TS = "2026-11-17T07:00:00+07:00"


class TestSnapSignature(SnapCommon):
    def test_timestamp_jakarta(self):
        self.assertEqual(
            self.provider._snap_timestamp(datetime(2026, 11, 17, 0, 0, 0)), TS
        )

    def test_timestamp_default_now_format(self):
        ts = self.provider._snap_timestamp()
        self.assertRegex(ts, r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\+07:00$")

    def test_minify(self):
        self.assertEqual(
            self.provider._snap_minify(
                {"partnerReferenceNo": "1", "accountNo": "1234567890"}
            ),
            BODY,
        )
        self.assertEqual(self.provider._snap_minify(None), b"")

    def test_string_to_sign(self):
        self.assertEqual(
            self.provider._snap_symmetric_string_to_sign(
                "post", "/openapi/v1.0/bank-statement", "TKN", BODY, TS
            ),
            "POST:/openapi/v1.0/bank-statement:TKN:"
            "2df1af490039021deb53ef2e776820562560dae8808eaabf2162d98fd9613b69:"
            "2026-11-17T07:00:00+07:00",
        )

    def test_string_to_sign_empty_body(self):
        sts = self.provider._snap_symmetric_string_to_sign("GET", "/x", "TKN", b"", TS)
        self.assertIn(
            ":e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855:", sts
        )

    def test_symmetric_signature(self):
        sts = self.provider._snap_symmetric_string_to_sign(
            "POST", "/openapi/v1.0/bank-statement", "TKN", BODY, TS
        )
        expected = base64.b64encode(
            hmac.new(b"test-secret", sts.encode(), hashlib.sha512).digest()
        ).decode()
        self.assertEqual(
            self.provider._snap_sign_symmetric(
                "POST", "/openapi/v1.0/bank-statement", "TKN", BODY, TS
            ),
            expected,
        )

    def test_asymmetric_signature_verifies(self):
        signature = self.provider._snap_sign_asymmetric(TS)
        public_key = serialization.load_pem_public_key(TEST_PUBLIC_KEY.encode())
        # Raises InvalidSignature when wrong.
        public_key.verify(
            base64.b64decode(signature),
            f"test-client|{TS}".encode(),
            padding.PKCS1v15(),
            hashes.SHA256(),
        )

    def test_external_id_numeric(self):
        ids = [self.provider._snap_external_id() for _i in range(50)]
        for value in ids:
            self.assertTrue(value.isdigit())
            self.assertLessEqual(len(value), 32)
        self.assertEqual(len(set(ids)), 50)
