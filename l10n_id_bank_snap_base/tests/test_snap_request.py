# Copyright 2026 PT Solusi Aglis Indonesia. (http://solusiaglis.co.id)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
import base64
from datetime import timedelta
from unittest import mock

import requests
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding

from odoo import fields
from odoo.exceptions import UserError

from .common import (
    REQUEST_PATH,
    TEST_PUBLIC_KEY,
    TOKEN_VALUE,
    SnapCommon,
    fake_response,
    token_response,
)

OK = {"responseCode": "2001400", "responseMessage": "Successful"}


class TestSnapRequest(SnapCommon):
    def _cred(self):
        return self.provider.sudo()

    def test_token_fetched_and_cached(self):
        with mock.patch(REQUEST_PATH, return_value=token_response()) as req:
            self.assertEqual(self._cred()._snap_get_token(), TOKEN_VALUE)
            self.assertEqual(self._cred()._snap_get_token(), TOKEN_VALUE)
        self.assertEqual(req.call_count, 1)
        args, kwargs = req.call_args
        self.assertEqual(args[0], "POST")
        self.assertEqual(args[1], "https://snap.test/openapi/v1.0/access-token/b2b")
        self.assertEqual(kwargs["data"], b'{"grantType":"client_credentials"}')

    def test_token_headers(self):
        with mock.patch(REQUEST_PATH, return_value=token_response()) as req:
            self._cred()._snap_get_token()
        headers = req.call_args.kwargs["headers"]
        self.assertEqual(headers["X-CLIENT-KEY"], "test-client")
        public_key = serialization.load_pem_public_key(TEST_PUBLIC_KEY.encode())
        public_key.verify(
            base64.b64decode(headers["X-SIGNATURE"]),
            f"test-client|{headers['X-TIMESTAMP']}".encode(),
            padding.PKCS1v15(),
            hashes.SHA256(),
        )

    def test_token_refresh_near_expiry(self):
        cred = self._cred()
        cred.write(
            {
                "snap_access_token": "old",
                "snap_token_expiry": fields.Datetime.now() + timedelta(seconds=30),
            }
        )
        with mock.patch(REQUEST_PATH, return_value=token_response()) as req:
            self.assertEqual(cred._snap_get_token(), TOKEN_VALUE)
        self.assertEqual(req.call_count, 1)

    def test_request_headers_and_signature(self):
        with mock.patch(
            REQUEST_PATH, side_effect=[token_response(), fake_response(OK)]
        ) as req:
            result = self._cred()._snap_request("/x", {"a": 1})
        self.assertEqual(result["responseCode"], "2001400")
        args, kwargs = req.call_args
        self.assertEqual(args[1], "https://snap.test/x")
        headers = kwargs["headers"]
        self.assertEqual(headers["Authorization"], f"Bearer {TOKEN_VALUE}")
        self.assertEqual(headers["CHANNEL-ID"], "95051")
        self.assertEqual(headers["X-PARTNER-ID"], "KBCABCINDO")
        self.assertTrue(headers["X-EXTERNAL-ID"].isdigit())
        self.assertEqual(
            headers["X-SIGNATURE"],
            self._cred()._snap_sign_symmetric(
                "POST", "/x", TOKEN_VALUE, kwargs["data"], headers["X-TIMESTAMP"]
            ),
        )

    def test_token_expired_retries_once(self):
        expired = fake_response(
            {"responseCode": "4011401", "responseMessage": "Invalid token (B2B)"}, 401
        )
        with mock.patch(
            REQUEST_PATH,
            side_effect=[
                token_response(),
                expired,
                token_response("t2"),
                fake_response(OK),
            ],
        ) as req:
            self._cred()._snap_request("/x", {})
        self.assertEqual(req.call_count, 4)
        self.assertEqual(req.call_args.kwargs["headers"]["Authorization"], "Bearer t2")

    def test_token_expired_twice_raises(self):
        expired = fake_response(
            {"responseCode": "4011401", "responseMessage": "Invalid token (B2B)"}, 401
        )
        with mock.patch(
            REQUEST_PATH,
            side_effect=[token_response(), expired, token_response("t2"), expired],
        ) as req:
            with self.assertRaises(UserError):
                self._cred()._snap_request("/x", {})
        self.assertEqual(req.call_count, 4)

    def test_unknown_client_message(self):
        response = fake_response(
            {
                "responseCode": "4017300",
                "responseMessage": "Unauthorized. [Unknown client]",
            },
            401,
        )
        with mock.patch(REQUEST_PATH, return_value=response):
            with self.assertRaises(UserError) as ctx:
                self._cred()._snap_get_token()
        message = str(ctx.exception)
        self.assertIn("4017300", message)
        self.assertIn("Unknown client", message)
        self.assertIn("Client ID", message)

    def test_error_never_leaks_secrets(self):
        cases = [
            [fake_response({"responseCode": "4017300", "responseMessage": "x"}, 401)],
            [token_response(), fake_response({"responseCode": "4031401"}, 403)],
            [token_response(), fake_response({"responseCode": "4291400"}, 429)],
            [token_response(), fake_response({"responseCode": "5001401"}, 500)],
            [token_response(), requests.Timeout("boom")],
        ]
        for side_effect in cases:
            self._cred().write({"snap_access_token": False, "snap_token_expiry": False})
            with mock.patch(REQUEST_PATH, side_effect=side_effect):
                with self.assertRaises(UserError) as ctx:
                    self._cred()._snap_request("/x", {})
            message = str(ctx.exception)
            for secret in ("test-secret", TOKEN_VALUE, "PRIVATE KEY", "Bearer"):
                self.assertNotIn(secret, message)

    def test_error_hints(self):
        for code, hint in (
            ("4031401", "not enabled"),
            ("4091400", "X-EXTERNAL-ID"),
            ("4291400", "20000"),
            ("5001401", "retry"),
        ):
            self._cred().write({"snap_access_token": False, "snap_token_expiry": False})
            with mock.patch(
                REQUEST_PATH,
                side_effect=[token_response(), fake_response({"responseCode": code})],
            ):
                with self.assertRaises(UserError) as ctx:
                    self._cred()._snap_request("/x", {})
            self.assertIn(code, str(ctx.exception))
            self.assertIn(hint, str(ctx.exception))

    def test_timeout_is_user_error(self):
        with mock.patch(REQUEST_PATH, side_effect=requests.Timeout("boom")):
            with self.assertRaises(UserError) as ctx:
                self._cred()._snap_get_token()
        self.assertIn("snap.test", str(ctx.exception))

    def test_token_cleared_on_connection_change(self):
        cred = self._cred()
        for vals in (
            {"snap_environment": "production"},
            {"snap_base_url": "https://other.test"},
            {"snap_client_key": "other"},
            {"snap_client_secret": "other"},
        ):
            cred.write(
                {
                    "snap_access_token": "old",
                    "snap_token_expiry": fields.Datetime.now() + timedelta(hours=1),
                }
            )
            cred.write(vals)
            self.assertFalse(cred.snap_access_token, vals)
        cred.write({"snap_access_token": "kept"})
        cred.write({"name": "Renamed"})
        self.assertEqual(cred.snap_access_token, "kept")

    def test_production_without_url_raises(self):
        cred = self._cred()
        cred.snap_base_url = False
        with mock.patch(REQUEST_PATH) as req:
            with self.assertRaises(UserError):
                cred._snap_get_token()
        req.assert_not_called()
