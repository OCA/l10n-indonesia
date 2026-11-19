Core of the SNAP BI (Standar Nasional Open API Pembayaran, Bank Indonesia)
integration for Online Bank Statements.

This module adds the SNAP connection data (Client ID, Client Secret, RSA key
pair) to the online bank statement provider, the SNAP signatures, B2B access
token handling and the standard SNAP *Bank Statement* and *Balance Inquiry*
calls. It does not add any bank by itself: install a bank module such as
`account_statement_import_online_bca`.

**Adding a bank.** A bank module depends on this module and only declares
its configuration in `_snap_bank_config()` (see `account_statement_import_online_bca`):

```python
@api.model
def _snap_bank_config(self):
    config = super()._snap_bank_config()
    config["mybank_snap"] = {
        "label": "My Bank (SNAP BI)",  # registers the provider service
        "sandbox_url": "https://sandbox.mybank.example",
        "production_url": False,  # typed in on the provider when unpublished
        "channel_id": "12345",
        "token_path": "/openapi/v1.0/access-token/b2b",
        "statement_path": "/openapi/v1.0/bank-statement",
        "balance_path": "/openapi/v1.0/balance-inquiry",
        "history_days": 31,  # optional: older periods are refused / skipped
        "remark_split": 18,  # optional: fixed-width remark parts
        "sandbox_partner_reference_no": "...",  # optional: sandbox-only value
    }
    return config
```

Its tests reuse the standard SNAP tests:

```python
from odoo.addons.l10n_id_bank_snap_base.tests.common import (
    SnapBankCase,
    SnapBankTestsMixin,
)


class TestMyBank(SnapBankTestsMixin, SnapBankCase):
    snap_service = "mybank_snap"
```

Banks that deviate from the standard override the relevant `_snap_*` method.
