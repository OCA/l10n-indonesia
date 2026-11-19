# Copyright 2026 PT Solusi Aglis Indonesia. (http://solusiaglis.co.id)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
import json
from datetime import timedelta
from unittest import mock

import pytz

from odoo import fields
from odoo.exceptions import UserError
from odoo.tests import TransactionCase

from odoo.addons.l10n_id_bank_snap_base.tests.common import (
    REQUEST_PATH,
    SAMPLE_STATEMENT,
    TEST_PRIVATE_KEY,
    SnapBankCase,
    SnapBankTestsMixin,
    fake_response,
    jakarta_day,
    statement_on,
    token_response,
)

# Yesterday in Jakarta, in naive UTC: always inside BCA's 31-day window.
SINCE, UNTIL = jakarta_day(1)
DAY = pytz.utc.localize(SINCE).astimezone(pytz.timezone("Asia/Jakarta")).date()
DOC_REMARK = (
    "TRSF E-BANKING DB 1111/ATRTG/WS95051 09112016123456 pencairan merchant "
    "SITI KHADIJAH"
)


class TestBca(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))
        cls.journal = cls.env["account.journal"].create(
            {
                "name": "BCA",
                "type": "bank",
                "code": "BCA1",
                "bank_statements_source": "online",
                "suspense_account_id": cls.env["account.account"]
                .create(
                    {
                        "name": "BCA Suspense",
                        "code": "BCASUSP",
                        "account_type": "asset_current",
                        "reconcile": True,
                    }
                )
                .id,
                "bank_account_id": cls.env["res.partner.bank"]
                .create(
                    {
                        "acc_number": "1234567890",
                        "partner_id": cls.env.company.partner_id.id,
                    }
                )
                .id,
            }
        )
        cls.provider = cls.env["online.bank.statement.provider"].create(
            {
                "service": "bca_snap",
                "journal_id": cls.journal.id,
                "statement_creation_mode": "daily",
                "snap_client_key": "test-client",
                "snap_client_secret": "test-secret",
                "snap_partner_id": "KBBABCINDO",
                "snap_private_key": TEST_PRIVATE_KEY,
            }
        )

    def _bank(self, statement):
        def bank(method, url, **kwargs):
            if url.endswith("/access-token/b2b"):
                return token_response()
            return fake_response(statement)

        return mock.patch(REQUEST_PATH, side_effect=bank)

    def _statement_payloads(self, req):
        return [
            json.loads(c.kwargs["data"])
            for c in req.call_args_list
            if c.args[1].endswith("/openapi/v1.0/bank-statement")
        ]

    def test_service_registered(self):
        services = self.env["online.bank.statement.provider"]._get_available_services()
        self.assertIn(("bca_snap", "BCA (SNAP BI)"), services)
        self.assertTrue(self.provider.snap_is_snap)

    def test_provider_snap_defaults(self):
        self.assertEqual(self.provider.snap_base_url, "https://sandbox.bca.co.id")
        self.assertEqual(self.provider.snap_channel_id, "95051")

    def test_sandbox_uses_bca_sample_reference(self):
        with self._bank(SAMPLE_STATEMENT) as req:
            self.provider._pull(SINCE, UNTIL)
        payload = self._statement_payloads(req)[0]
        self.assertEqual(payload["partnerReferenceNo"], "2020102900000000000001")

    def test_production_uses_own_reference(self):
        self.provider.write(
            {"snap_environment": "production", "snap_base_url": "https://bca.test"}
        )
        with self._bank(SAMPLE_STATEMENT) as req:
            self.provider._pull(SINCE, UNTIL)
        ref = self._statement_payloads(req)[0]["partnerReferenceNo"]
        self.assertNotEqual(ref, "2020102900000000000001")
        self.assertEqual(len(ref), 22)

    def test_production_without_url_raises(self):
        self.provider.snap_environment = "production"
        self.assertFalse(self.provider.snap_base_url)
        with mock.patch(REQUEST_PATH) as req:
            with self.assertRaises(UserError):
                self.provider.sudo()._snap_get_token()
        req.assert_not_called()

    def test_bca_date_range_one_jakarta_day(self):
        with self._bank(SAMPLE_STATEMENT) as req:
            self.provider._pull(SINCE, UNTIL)
        payloads = self._statement_payloads(req)
        self.assertEqual(len(payloads), 1)
        self.assertEqual(payloads[0]["fromDateTime"], f"{DAY}T00:00:00+07:00")
        self.assertEqual(
            payloads[0]["toDateTime"], f"{DAY + timedelta(days=1)}T00:00:00+07:00"
        )

    def test_remark_split(self):
        self.assertEqual(
            self.provider._snap_clean_remark(DOC_REMARK),
            "TRSF E-BANKING DB / 1111/ATRTG/WS95051 09112016123456 pencairan "
            "merchant SITI KHADIJAH",
        )
        self.assertEqual(self.provider._snap_clean_remark("BIAYA  ADM"), "BIAYA ADM")

    def _days_ago(self, days):
        return fields.Datetime.now().replace(
            hour=17, minute=0, second=0, microsecond=0
        ) - timedelta(days=days)

    def test_bca_window_scheduled_clamps_and_posts(self):
        provider = self.provider.with_context(scheduled=True)
        messages = len(self.provider.message_ids)
        with self._bank(SAMPLE_STATEMENT) as req:
            result = provider._obtain_statement_data(
                self._days_ago(40), self._days_ago(35)
            )
        self.assertEqual(result, ([], {}))
        req.assert_not_called()
        self.assertEqual(len(self.provider.message_ids), messages + 1)
        self.assertIn("31", self.provider.message_ids[0].body)

        with self._bank(SAMPLE_STATEMENT) as req:
            provider._obtain_statement_data(self._days_ago(40), self._days_ago(1))
        payload = self._statement_payloads(req)[0]
        cutoff = self.provider._snap_history_cutoff()
        expected = self.provider._snap_request_date_range(
            cutoff, cutoff + timedelta(days=1)
        )[0]
        self.assertEqual(payload["fromDateTime"], expected)
        self.assertEqual(len(self.provider.message_ids), messages + 2)

    def test_bca_window_manual_raises(self):
        with self._bank(SAMPLE_STATEMENT):
            with self.assertRaises(UserError) as ctx:
                self.provider._obtain_statement_data(
                    self._days_ago(40), self._days_ago(35)
                )
        self.assertIn("31", str(ctx.exception))

    def test_bca_window_recent_untouched(self):
        with self._bank(SAMPLE_STATEMENT) as req:
            self.provider._obtain_statement_data(self._days_ago(3), self._days_ago(2))
        self.assertEqual(len(self._statement_payloads(req)), 1)

    def test_pull_end_to_end_mocked(self):
        with self._bank(statement_on(SINCE)):
            self.provider._pull(SINCE, UNTIL)
        lines = self.env["account.bank.statement.line"].search(
            [("journal_id", "=", self.journal.id)]
        )
        self.assertEqual(len(lines), 3)
        self.assertEqual(sum(lines.mapped("amount")), 175000.0)


class TestBcaStandard(SnapBankTestsMixin, SnapBankCase):
    snap_service = "bca_snap"
