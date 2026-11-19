# Copyright 2026 PT Solusi Aglis Indonesia. (http://solusiaglis.co.id)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
import json
from datetime import datetime, time, timedelta
from unittest import mock

import pytz

from odoo.exceptions import AccessError, UserError
from odoo.tests import new_test_user

from odoo.addons.l10n_id_bank_snap_base.models.online_bank_statement_provider import (
    SNAP_TZ,
)

from .common import (
    ITEM_DEBIT,
    ITEM_TWIN,
    REMARK,
    REQUEST_PATH,
    SAMPLE_BALANCE,
    SAMPLE_STATEMENT,
    TOKEN_VALUE,
    SnapCommon,
    fake_response,
    sample_statement,
    token_response,
)

# One Jakarta day (2026-11-17 00:00 to 24:00 WIB) expressed in naive UTC, as
# account_statement_import_online passes daily periods to the provider.
SINCE = datetime(2026, 11, 16, 17, 0)
UNTIL = datetime(2026, 11, 17, 17, 0)


class TestSnapStatement(SnapCommon):
    def _lines(self):
        return self.env["account.bank.statement.line"].search(
            [("journal_id", "=", self.journal.id)]
        )

    def _pull(self, statement, provider=None):
        """Pull one Jakarta day; the fake bank answers by endpoint."""

        def bank(method, url, **kwargs):
            if url.endswith("/access-token/b2b"):
                return token_response()
            self.assertTrue(url.endswith("/bank-statement"))
            return fake_response(statement)

        with mock.patch(REQUEST_PATH, side_effect=bank) as req:
            (provider or self.provider)._pull(SINCE, UNTIL)
        statement_calls = [
            c for c in req.call_args_list if c.args[1].endswith("/bank-statement")
        ]
        self.assertEqual(len(statement_calls), 1)
        return req

    def test_provider_defaults(self):
        self.assertEqual(self.provider.account_number, "1234567890")
        self.assertEqual(self.provider.tz, "Asia/Jakarta")
        self.assertTrue(self.provider.snap_is_snap)

    def test_detail_to_line_credit_debit(self):
        credit = self.provider._snap_detail_to_line(ITEM_TWIN)
        debit = self.provider._snap_detail_to_line(ITEM_DEBIT)
        self.assertEqual(credit["amount"], 100000.0)
        self.assertEqual(debit["amount"], -25000.0)
        self.assertEqual(credit["payment_ref"], REMARK)
        self.assertEqual(credit["date"].utcoffset(), timedelta(hours=7))
        self.assertEqual(json.loads(credit["raw_data"]), ITEM_TWIN)

    def test_naive_transaction_date_is_jakarta(self):
        line = self.provider._snap_detail_to_line(
            dict(ITEM_DEBIT, transactionDate="2026-11-17T18:30:00")
        )
        self.assertEqual(line["date"].utcoffset(), timedelta(hours=7))
        late = dict(ITEM_DEBIT, transactionDate="2026-11-17T18:30:00")
        self._pull(sample_statement([late, ITEM_TWIN]))
        self.assertEqual(len(self._lines()), 2)

    def test_iso_type_codes(self):
        for code in ("DEBIT", "DBIT", "DB", "D", "dbit"):
            line = self.provider._snap_detail_to_line(dict(ITEM_DEBIT, type=code))
            self.assertEqual(line["amount"], -25000.0, code)
        for code in ("CREDIT", "CRDT", "CR", "C"):
            line = self.provider._snap_detail_to_line(dict(ITEM_DEBIT, type=code))
            self.assertEqual(line["amount"], 25000.0, code)

    def test_dbit_rows_are_imported(self):
        self._pull(sample_statement([ITEM_TWIN, dict(ITEM_DEBIT, type="DBIT")]))
        self.assertEqual(sorted(self._lines().mapped("amount")), [-25000.0, 100000.0])

    def test_has_more_production_raises(self):
        self.provider.snap_environment = "production"
        self.provider.snap_base_url = "https://snap.test"
        with self.assertRaises(UserError) as ctx:
            self._pull(dict(SAMPLE_STATEMENT, hasMore="Y"))
        self.assertIn("hasMore", str(ctx.exception))
        self.assertFalse(self._lines())

    def test_has_more_sandbox_imports(self):
        self._pull(dict(SAMPLE_STATEMENT, hasMore="Y"))
        self.assertEqual(len(self._lines()), 3)

    def test_unknown_type_skipped_and_posted(self):
        odd = dict(ITEM_DEBIT, type="XFER", remark="ODD ROW")
        self._pull(sample_statement([ITEM_TWIN, odd]))
        self.assertEqual(len(self._lines()), 1)
        body = self.provider.message_ids[0].body
        self.assertIn("XFER", body)
        self.assertIn("ODD ROW", body)

    def test_unique_id_twins(self):
        items = SAMPLE_STATEMENT["detailData"]
        pairs = [(self.provider._snap_detail_to_line(i), i) for i in items]
        self.provider._snap_assign_unique_ids(pairs)
        ids = [line["unique_import_id"] for line, _item in pairs]
        self.assertEqual(len(set(ids)), 3)
        twins = sorted(ids[:2])
        self.assertEqual(twins[0][:-2], twins[1][:-2])
        self.assertEqual([twins[0][-2:], twins[1][-2:]], ["-0", "-1"])

    def test_request_payload(self):
        req = self._pull(SAMPLE_STATEMENT)
        args, kwargs = req.call_args
        self.assertEqual(args[1], "https://snap.test/openapi/v1.0/bank-statement")
        payload = json.loads(kwargs["data"])
        self.assertEqual(payload["accountNo"], "1234567890")
        self.assertEqual(payload["fromDateTime"], "2026-11-17T00:00:00+07:00")
        self.assertEqual(payload["toDateTime"], "2026-11-18T00:00:00+07:00")
        self.assertTrue(payload["partnerReferenceNo"])

    def test_repull_no_duplicates(self):
        self._pull(SAMPLE_STATEMENT)
        self.assertEqual(len(self._lines()), 3)
        self._pull(SAMPLE_STATEMENT)
        self.assertEqual(len(self._lines()), 3)

    def test_repull_adds_only_new_twin(self):
        self._pull(sample_statement([ITEM_TWIN, ITEM_DEBIT]))
        self.assertEqual(len(self._lines()), 2)
        self._pull(SAMPLE_STATEMENT)
        self.assertEqual(len(self._lines()), 3)
        self.assertEqual(sum(self._lines().mapped("amount")), 175000.0)

    def test_balances_from_response(self):
        self._pull(SAMPLE_STATEMENT)
        statement = self._lines().statement_id
        self.assertEqual(len(statement), 1)
        self.assertEqual(statement.balance_start, 1000000.0)
        self.assertEqual(statement.balance_end_real, 1175000.0)

    def test_request_date_range_default(self):
        # toDateTime is the (exclusive) next Jakarta midnight: never an empty
        # window; the framework drops and balances out the extra rows.
        self.assertEqual(
            self.provider._snap_request_date_range(SINCE, UNTIL),
            ("2026-11-17T00:00:00+07:00", "2026-11-18T00:00:00+07:00"),
        )
        week_since = datetime(2026, 10, 1, 17, 0)
        self.assertEqual(
            self.provider._snap_request_date_range(
                week_since, week_since + timedelta(days=7)
            ),
            ("2026-10-02T00:00:00+07:00", "2026-10-09T00:00:00+07:00"),
        )

    def test_request_date_range_never_future(self):
        today = datetime.now(SNAP_TZ).date()
        since = SNAP_TZ.localize(datetime.combine(today, time.min))
        since = since.astimezone(pytz.utc).replace(tzinfo=None)
        from_dt, to_dt = self.provider._snap_request_date_range(
            since, since + timedelta(days=1)
        )
        self.assertEqual(from_dt, f"{today.isoformat()}T00:00:00+07:00")
        self.assertEqual(to_dt, f"{today.isoformat()}T00:00:00+07:00")

    def test_missing_client_id_raises(self):
        self.provider.snap_client_key = False
        with mock.patch(REQUEST_PATH) as req:
            with self.assertRaises(UserError):
                self.provider._pull(SINCE, UNTIL)
        req.assert_not_called()

    def test_test_token_notification(self):
        with mock.patch(REQUEST_PATH, return_value=token_response()):
            action = self.provider.action_snap_test_token()
        text = json.dumps(action)
        self.assertEqual(action["tag"], "display_notification")
        self.assertIn("2007300", text)
        self.assertNotIn(TOKEN_VALUE, text)

    def test_test_connection_posts_message(self):
        with mock.patch(
            REQUEST_PATH,
            side_effect=[token_response(), fake_response(SAMPLE_BALANCE)],
        ) as req:
            action = self.provider.action_snap_test_connection()
        self.assertEqual(action["params"]["type"], "success")
        self.assertEqual(
            req.call_args.args[1], "https://snap.test/openapi/v1.0/balance-inquiry"
        )
        body = self.provider.message_ids[0].body
        self.assertIn("ANDHIKA", body)
        self.assertIn("2001100", body)
        self.assertNotIn("test-secret", body)
        self.assertNotIn(TOKEN_VALUE, body)

    def test_test_connection_account_infos_object(self):
        balance = dict(SAMPLE_BALANCE, accountInfos=SAMPLE_BALANCE["accountInfos"][0])
        with mock.patch(
            REQUEST_PATH,
            side_effect=[token_response(), fake_response(balance)],
        ):
            action = self.provider.action_snap_test_connection()
        self.assertEqual(action["params"]["type"], "success")
        self.assertIn("200000.00", action["params"]["message"])

    def test_partner_reference_no(self):
        with mock.patch(
            REQUEST_PATH,
            side_effect=[token_response(), fake_response(SAMPLE_BALANCE)],
        ) as req:
            self.provider.action_snap_test_connection()
        ref = json.loads(req.call_args.kwargs["data"])["partnerReferenceNo"]
        self.assertTrue(ref.isdigit())
        self.assertEqual(len(ref), 22)

    def test_test_connection_failure_notifies(self):
        with mock.patch(
            REQUEST_PATH,
            return_value=fake_response({"responseCode": "4017300"}, 401),
        ):
            action = self.provider.action_snap_test_connection()
        self.assertEqual(action["params"]["type"], "danger")
        self.assertIn("4017300", action["params"]["message"])

    def test_account_user_can_pull_but_not_read_secrets(self):
        user = new_test_user(
            self.env,
            login="snap_pull_user",
            groups="account.group_account_user",
        )
        self._pull(SAMPLE_STATEMENT, provider=self.provider.with_user(user))
        self.assertEqual(len(self._lines()), 3)
        with self.assertRaises(AccessError):
            self.provider.with_user(user).read(["snap_client_secret"])
