# Copyright 2026 PT Solusi Aglis Indonesia. (http://solusiaglis.co.id)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
import json
from datetime import datetime, time, timedelta
from unittest import mock

import pytz

from odoo.tests import TransactionCase

from odoo.addons.l10n_id_bank_snap_base.models.online_bank_statement_provider import (
    SNAP_TZ,
)

REQUEST_PATH = (
    "odoo.addons.l10n_id_bank_snap_base.models."
    "online_bank_statement_provider.requests.request"
)

TOKEN_VALUE = "tok-SECRET-123"

REMARK = "TRSF E-BANKING DB 1111/ATRTG/WS95051 09112016123456 pencairan merchant"
ITEM_TWIN = {
    "amount": {"value": "100000.00", "currency": "IDR"},
    "transactionDate": "2026-11-17T12:00:00+07:00",
    "remark": REMARK,
    "type": "CREDIT",
}
ITEM_DEBIT = {
    "amount": {"value": "25000.00", "currency": "IDR"},
    "transactionDate": "2026-11-17T11:00:00+07:00",
    "remark": "BIAYA ADM",
    "type": "DEBIT",
}


def sample_statement(details):
    return {
        "responseCode": "2001400",
        "responseMessage": "Successful",
        "referenceNo": "2020102977770000000009",
        "partnerReferenceNo": "2020102900000000000001",
        "balance": [
            {
                "amount": {"value": "1175000.00", "currency": "IDR"},
                "startingBalance": {"value": "1000000.00", "currency": "IDR"},
                "endingBalance": {"value": "1175000.00", "currency": "IDR"},
            }
        ],
        "detailData": details,
    }


# Newest first, as BCA returns it.
SAMPLE_STATEMENT = sample_statement([ITEM_TWIN, dict(ITEM_TWIN), ITEM_DEBIT])

SAMPLE_BALANCE = {
    "responseCode": "2001100",
    "responseMessage": "Successful",
    "referenceNo": "2020102977770000000009",
    "partnerReferenceNo": "2020102900000000000001",
    "accountNo": "1234567890",
    "name": "ANDHIKA",
    "accountInfos": [
        {
            "amount": {"value": "100000.00", "currency": "IDR"},
            "floatAmount": {"value": "500000.00", "currency": "IDR"},
            "holdAmount": {"value": "200000.00", "currency": "IDR"},
            "availableBalance": {"value": "200000.00", "currency": "IDR"},
        }
    ],
}


def fake_response(payload, status=200):
    response = mock.Mock()
    response.status_code = status
    response.text = json.dumps(payload)
    response.json.return_value = payload
    return response


def token_response(token=TOKEN_VALUE, expires="900"):
    return fake_response(
        {
            "responseCode": "2007300",
            "responseMessage": "Successful",
            "accessToken": token,
            "tokenType": "bearer",
            "expiresIn": expires,
        }
    )


# Fixed RSA 2048 test key pair. Test-only material, never used against a bank.
TEST_PRIVATE_KEY = """-----BEGIN PRIVATE KEY-----
MIIEvgIBADANBgkqhkiG9w0BAQEFAASCBKgwggSkAgEAAoIBAQDNmjBKNmgBTdQ3
3jMZsxTsBb5Mzq8OruBOtA5waouGLTpyMx0N/rJ26iLoTsimG0fKj/9V9VQHMGyb
rRnIBmaZOHV3/gAdzMg0RuP3u+q/miZxibzYuQJGvMQgiwuUlEVdLwqj0u04lkNJ
Uz3lpN6fTlE7jf8P1JlgDp04xxHH+pS8B0L40lJCCO6W+SieKvlpKZQSCjnCSZbu
DcrRLdmeBOusIacoulM++Ms87HWUFo9AIJxyZAe+5y348yvA3PNup8pep00eaB67
kR60N4U8MV00q44ThHTNQAmFmmJ1iiutl9s/AMSThpX36CqXRtpC+hvSQbZyt2Z9
ydPZVPqvAgMBAAECggEAWGX2ZDoPLpxZZanl+6M5GB+CCgEFWEFNFNmqqZ/NnGN+
0RHz6Iv9DE6vsoUJFQ3+qHOQG1OvDKY/1BExWASUgUU6kFxHjYh5/awLIP0NOdMb
u042wVGOTn6jrsBJutijGCT9JKGwN9e3V2PwZXek9gaUu4/aPeKxDRFLfNluZjWs
ACXdXR6CXiztipLaQ9Y4DiMDGbu7Tj72OlP8ZGnnwzO3SHqV6/ZstpzZ7gdfvXBu
sIONRnwchKpTx2z1kmMhvV7Rf45vXQdKYOc42PSC5BDY2AbLZUr/4xGJoidFRU29
dRbocmAX7TIqwVf7IpKoC6dq7VGqbzBhFVCrQd/3uQKBgQDqfZxKEIG64JVzf7oD
U0ppSzy+AhE/5VY90UeWgl7F9omZZKdFLOIuUr56OjP5Q8vuTxCgXm4DEkB3Hcyp
6L+haoS+XECcQZ3OR6QFgnDcwE2RtY/WLMXp4cATXxSzqBXv9s2L0LZdHfSCnqhG
+ux+GaG4dm35K1SmtTA/hGaRZwKBgQDgdjYw/IWG2AQAr18Lpcn92Zp1O+WUIY0M
W4K1OV6YVscMFa7UDahJN9I2a02KX/Gg1nC/ytkvp38qqLhyxxY/EHS71BpuDedg
/aTrE3bdGb1UJ1WUHRtfziC8rzhN6FUrGmlR+gaysRLdOkVuajfETGtUhTNXXusT
WkVO86YXeQKBgQCT50DCMqExN2Ds5f51BH8l5O/eRT2OGOCJw0wtMfQHV5a46xTa
fBH59/Tu8XFA4zNpD/PDw2wOgd+pgmFKNmVQsfgifdu+82BO8T8SvpDjnGQQ6P1d
sQXwnJTjYxCStQ2JOxmw+6dbGn7UOLCZfMHYU+B+kiyRgnQ1ZomVNrTfNwKBgQC1
RCGdS8CVVctdtkI+SMOnodxPgnBzQOkEKr6SlWLkCWgzRStrih/2CQNU+TCkZ7jd
F2/0It9j0ZMroxdZcZdwlFyA9tflOos5U3ykbpKWGVxBIobE1wCtTOw5FBOXLuHg
rjKRhiV0lvVR/OXnNhYVC1W96te8XiXe+g5wpOjjmQKBgD0ae8S28VQUoun/bvKM
ICbzoF0GJO1Ncm6NvzWS/3VIfAy3FL7a0T056q5Yv8+RAVUOWH7CwE3cwu6Tresm
jqjR+arE47uTbf1o7p+Lx2PTT6W53m2fRghsGDyb5DFXFJ0KC6hRuBm61wZVnm5A
rAGMn7eLh+F2McWPqGdhr5fE
-----END PRIVATE KEY-----
"""

TEST_PUBLIC_KEY = """-----BEGIN PUBLIC KEY-----
MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAzZowSjZoAU3UN94zGbMU
7AW+TM6vDq7gTrQOcGqLhi06cjMdDf6yduoi6E7IphtHyo//VfVUBzBsm60ZyAZm
mTh1d/4AHczINEbj97vqv5omcYm82LkCRrzEIIsLlJRFXS8Ko9LtOJZDSVM95aTe
n05RO43/D9SZYA6dOMcRx/qUvAdC+NJSQgjulvkonir5aSmUEgo5wkmW7g3K0S3Z
ngTrrCGnKLpTPvjLPOx1lBaPQCCccmQHvuct+PMrwNzzbqfKXqdNHmgeu5EetDeF
PDFdNKuOE4R0zUAJhZpidYorrZfbPwDEk4aV9+gql0baQvob0kG2crdmfcnT2VT6
rwIDAQAB
-----END PUBLIC KEY-----
"""


SNAP_TEST_CONFIG = {
    "dummy": {
        "token_path": "/openapi/v1.0/access-token/b2b",
        "statement_path": "/openapi/v1.0/bank-statement",
        "balance_path": "/openapi/v1.0/balance-inquiry",
    }
}


def jakarta_day(days_ago):
    """(since, until) of one Jakarta day ``days_ago`` days back, naive UTC."""
    day = datetime.now(SNAP_TZ).date() - timedelta(days=days_ago)
    since = SNAP_TZ.localize(datetime.combine(day, time.min))
    since = since.astimezone(pytz.utc).replace(tzinfo=None)
    return since, since + timedelta(days=1)


def statement_on(since, details=None):
    """SAMPLE_STATEMENT with its rows dated on the Jakarta day of ``since``."""
    day = pytz.utc.localize(since).astimezone(SNAP_TZ).date().isoformat()
    rows = []
    for item in details or SAMPLE_STATEMENT["detailData"]:
        hour = item["transactionDate"][11:]
        rows.append(dict(item, transactionDate=f"{day}T{hour}"))
    return sample_statement(rows)


class SnapBankCase(TransactionCase):
    """A bank journal with an online provider on ``snap_service``.

    Bank modules subclass it, with :class:`SnapBankTestsMixin`, to run the
    standard SNAP tests against their own configuration.
    """

    snap_service = None
    snap_provider_vals = {}

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))
        cls._snap_start_patches()
        cls.provider = cls._new_provider("SNAPB", "1234567890")
        cls.journal = cls.provider.journal_id

    @classmethod
    def _snap_start_patches(cls):
        """Hook to patch the model before the test provider is created."""

    @classmethod
    def _new_provider(cls, code, account_number, **vals):
        journal = cls.env["account.journal"].create(
            {
                "name": f"SNAP Bank {code}",
                "type": "bank",
                "code": code,
                "bank_statements_source": "online",
                "suspense_account_id": cls.env["account.account"]
                .create(
                    {
                        "name": f"SNAP Suspense {code}",
                        "code": f"SUSP{code}",
                        "account_type": "asset_current",
                        "reconcile": True,
                    }
                )
                .id,
                "bank_account_id": cls.env["res.partner.bank"]
                .create(
                    {
                        "acc_number": account_number,
                        "partner_id": cls.env.company.partner_id.id,
                    }
                )
                .id,
            }
        )
        values = {
            "service": cls.snap_service,
            "journal_id": journal.id,
            "statement_creation_mode": "daily",
            "snap_client_key": "test-client",
            "snap_client_secret": "test-secret",
            "snap_partner_id": "KBCABCINDO",
            "snap_private_key": TEST_PRIVATE_KEY,
        }
        values.update(cls.snap_provider_vals)
        values.update(vals)
        return cls.env["online.bank.statement.provider"].create(values)

    def _fake_bank(self, statement=None, balance=None):
        """Patch HTTP: the fake bank answers by endpoint."""

        def bank(method, url, **kwargs):
            if url.endswith("/access-token/b2b"):
                return token_response()
            if "balance" in url:
                return fake_response(balance or SAMPLE_BALANCE)
            return fake_response(statement or SAMPLE_STATEMENT)

        return mock.patch(REQUEST_PATH, side_effect=bank)

    def _journal_lines(self):
        return self.env["account.bank.statement.line"].search(
            [("journal_id", "=", self.journal.id)]
        )


class SnapBankTestsMixin:
    """Standard tests every SNAP bank module runs on its own service."""

    # Odoo only collects test methods defined on the class itself otherwise.
    allow_inherited_tests_method = True

    def test_snap_service_listed(self):
        # The services offered on the provider form.
        services = dict(self.env["online.bank.statement.provider"]._selection_service())
        self.assertIn(self.snap_service, services)
        self.assertTrue(self.provider.snap_is_snap)
        self.assertTrue(self.provider.snap_base_url)

    def test_snap_pull_and_repull(self):
        since, until = jakarta_day(1)
        with self._fake_bank(statement_on(since)):
            self.provider._pull(since, until)
            self.provider._pull(since, until)
        self.assertEqual(len(self._journal_lines()), 3)

    def test_snap_test_connection(self):
        with self._fake_bank():
            action = self.provider.action_snap_test_connection()
        self.assertEqual(action["params"]["type"], "success", action)

    def test_snap_unknown_client(self):
        refused = fake_response(
            {"responseCode": "4017300", "responseMessage": "Unknown client"}, 401
        )
        with mock.patch(REQUEST_PATH, return_value=refused):
            action = self.provider.action_snap_test_connection()
        self.assertEqual(action["params"]["type"], "danger")
        self.assertIn("4017300", action["params"]["message"])


class SnapCommon(SnapBankCase):
    """SnapBankCase on the generic "dummy" service with a test configuration."""

    snap_service = "dummy"
    snap_provider_vals = {
        "snap_channel_id": "95051",
        "snap_base_url": "https://snap.test",
    }

    @classmethod
    def _snap_start_patches(cls):
        cls.startClassPatcher(
            mock.patch.object(
                type(cls.env["online.bank.statement.provider"]),
                "_snap_bank_config",
                return_value=SNAP_TEST_CONFIG,
            )
        )
