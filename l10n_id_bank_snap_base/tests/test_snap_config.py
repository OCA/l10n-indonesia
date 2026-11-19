# Copyright 2026 PT Solusi Aglis Indonesia. (http://solusiaglis.co.id)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from datetime import timedelta
from unittest import mock

from odoo import fields
from odoo.exceptions import UserError

from .common import (
    SAMPLE_STATEMENT,
    SNAP_TEST_CONFIG,
    SnapBankTestsMixin,
    SnapCommon,
)

REMARK = "TRSF E-BANKING DB 1111/ATRTG/WS95051 09112016123456 merchant"


class TestSnapStandardDummy(SnapBankTestsMixin, SnapCommon):
    """The standard bank tests also run on the generic test service."""


class TestSnapBankConfig(SnapCommon):
    def _config(self, **extra):
        """Patch the test service configuration with ``extra`` keys."""
        return mock.patch.object(
            type(self.env["online.bank.statement.provider"]),
            "_snap_bank_config",
            return_value={"dummy": dict(SNAP_TEST_CONFIG["dummy"], **extra)},
        )

    def test_services_from_config_label(self):
        Provider = self.env["online.bank.statement.provider"]
        with self._config(label="Dummy SNAP"):
            services = Provider._get_available_services()
        self.assertIn(("dummy", "Dummy SNAP"), services)
        self.assertEqual(len([s for s in services if s[0] == "dummy"]), 1)

    def test_remark_split_from_config(self):
        expected = "TRSF E-BANKING DB / 1111/ATRTG/WS95051 09112016123456 merchant"
        with self._config(remark_split=18):
            self.assertEqual(self.provider._snap_clean_remark(REMARK), expected)
        self.assertEqual(
            self.provider._snap_clean_remark(REMARK),
            "TRSF E-BANKING DB 1111/ATRTG/WS95051 09112016123456 merchant",
        )

    def _days_ago(self, days):
        return fields.Datetime.now().replace(
            hour=17, minute=0, second=0, microsecond=0
        ) - timedelta(days=days)

    def test_history_window_scheduled_clamps_and_posts(self):
        provider = self.provider.with_context(scheduled=True)
        messages = len(self.provider.message_ids)
        with self._config(history_days=31):
            with self._fake_bank(SAMPLE_STATEMENT) as req:
                result = provider._obtain_statement_data(
                    self._days_ago(40), self._days_ago(35)
                )
            self.assertEqual(result, ([], {}))
            req.assert_not_called()
            self.assertEqual(len(self.provider.message_ids), messages + 1)
            self.assertIn("31", self.provider.message_ids[0].body)
            cutoff = self.provider._snap_history_cutoff()
            self.assertLess(cutoff, self._days_ago(30))
            self.assertGreater(cutoff, self._days_ago(33))

    def test_history_window_manual_raises(self):
        with self._config(history_days=31):
            with self.assertRaises(UserError) as ctx:
                self.provider._obtain_statement_data(
                    self._days_ago(40), self._days_ago(35)
                )
        self.assertIn("31", str(ctx.exception))

    def test_no_history_limit_by_default(self):
        with self._fake_bank(SAMPLE_STATEMENT) as req:
            self.provider._obtain_statement_data(
                self._days_ago(400), self._days_ago(399)
            )
        self.assertTrue(req.called)
