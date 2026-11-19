# Copyright 2026 PT Solusi Aglis Indonesia. (http://solusiaglis.co.id)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
import base64

from odoo.exceptions import AccessError, UserError, ValidationError
from odoo.tests import new_test_user

from .common import TEST_PRIVATE_KEY, TEST_PUBLIC_KEY, SnapCommon


class TestSnapKeys(SnapCommon):
    def test_generate_key_pair(self):
        cred = self._new_provider("NEW", "1111111111", snap_private_key=False)
        cred.action_generate_key_pair()
        self.assertTrue(cred.snap_private_key.startswith("-----BEGIN PRIVATE KEY-----"))
        self.assertTrue(cred.snap_public_key.startswith("-----BEGIN PUBLIC KEY-----"))

    def test_regenerate_asks_confirmation(self):
        before = self.provider.snap_private_key
        with self.assertRaises(UserError):
            self.provider.action_generate_key_pair()
        self.assertEqual(self.provider.snap_private_key, before)
        self.provider.with_context(
            snap_confirm_regenerate=True
        ).action_generate_key_pair()
        self.assertNotEqual(self.provider.snap_private_key, before)

    def test_pasted_key_derives_public_key(self):
        cred = self._new_provider("PST", "2222222222", snap_private_key=False)
        cred.snap_private_key = TEST_PRIVATE_KEY
        self.assertEqual(cred.snap_public_key, TEST_PUBLIC_KEY)

    def test_single_line_key_accepted(self):
        # Keys copied from a bank portal often arrive on one line.
        one_line = " ".join(TEST_PRIVATE_KEY.split())
        cred = self._new_provider("ONE", "3333333333", snap_private_key=False)
        cred.snap_private_key = one_line
        self.assertEqual(cred.snap_public_key, TEST_PUBLIC_KEY)
        self.assertTrue(
            cred.snap_private_key.startswith("-----BEGIN PRIVATE KEY-----\n")
        )

    def test_bare_base64_key_accepted(self):
        body = "".join(TEST_PRIVATE_KEY.strip().splitlines()[1:-1])
        cred = self._new_provider("BAR", "4444444444", snap_private_key=body)
        self.assertEqual(cred.snap_public_key, TEST_PUBLIC_KEY)

    def test_uploaded_one_line_key_accepted(self):
        one_line = " ".join(TEST_PRIVATE_KEY.split())
        cred = self._new_provider("UPL", "5555555555", snap_private_key=False)
        cred.snap_private_key_file = base64.b64encode(one_line.encode())
        self.assertEqual(cred.snap_public_key, TEST_PUBLIC_KEY)

    def test_invalid_key_rejected(self):
        with self.assertRaises(ValidationError):
            self.provider.snap_private_key = "garbage"

    def test_secrets_not_copied(self):
        values = self.provider.copy_data()[0]
        for field in ("snap_client_secret", "snap_private_key", "snap_access_token"):
            self.assertNotIn(field, values)

    def test_account_user_cannot_read_or_write_secrets(self):
        user = new_test_user(
            self.env, login="snap_acc_user", groups="account.group_account_user"
        )
        provider = self.provider.with_user(user)
        self.assertEqual(
            provider.read(["snap_client_key"])[0]["snap_client_key"], "test-client"
        )
        for field in ("snap_client_secret", "snap_private_key"):
            with self.assertRaises(AccessError):
                provider.read([field])
        with self.assertRaises(AccessError):
            provider.write({"snap_client_secret": "x"})

    def test_shared_client_id_warning(self):
        other = self._new_provider("OTH", "6666666666")
        self.provider.snap_client_secret = "new-secret"
        result = self.provider._onchange_snap_shared_credentials()
        self.assertIn(other.name, result["warning"]["message"])
        lonely = self._new_provider("LON", "7777777777", snap_client_key="other")
        lonely.snap_client_secret = "x"
        self.assertFalse(lonely._onchange_snap_shared_credentials())

    def test_download_public_key_action(self):
        action = self.provider.action_download_public_key()
        self.assertEqual(action["type"], "ir.actions.act_url")
        self.assertIn("snap_public_key_file", action["url"])
