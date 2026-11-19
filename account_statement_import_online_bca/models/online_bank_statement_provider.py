# Copyright 2026 PT Solusi Aglis Indonesia. (http://solusiaglis.co.id)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import api, models


class OnlineBankStatementProvider(models.Model):
    _inherit = "online.bank.statement.provider"

    @api.model
    def _snap_bank_config(self):
        config = super()._snap_bank_config()
        config["bca_snap"] = {
            "label": "BCA (SNAP BI)",
            "sandbox_url": "https://sandbox.bca.co.id",
            # Not published in the BCA developer documentation: BCA gives it
            # on go-live, fill it in on the provider.
            "production_url": False,
            "channel_id": "95051",
            "token_path": "/openapi/v1.0/access-token/b2b",
            "statement_path": "/openapi/v1.0/bank-statement",
            "balance_path": "/openapi/v1.0/balance-inquiry",
            # BCA serves the last 31 days only.
            "history_days": 31,
            # BCA remarks are 2 fixed parts of 18 characters.
            "remark_split": 18,
            # The BCA sandbox only accepts its documented sample value.
            "sandbox_partner_reference_no": "2020102900000000000001",
        }
        return config
