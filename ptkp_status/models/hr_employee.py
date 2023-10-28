# Copyright (C) 2022 Panca Putra Pakpahan (<https://solusiaglis.co.id>).
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class HrEmployee(models.Model):
    _inherit = "hr.employee"

    ptkp_status = fields.Selection(
        [
            ("tk0", "TK/0"),
            ("tk1", "TK/1"),
            ("tk2", "TK/2"),
            ("tk3", "TK/3"),
            ("k0", "K/0"),
            ("k1", "K/1"),
            ("k2", "K/2"),
            ("k3", "K/3"),
        ],
        groups="hr.group_hr_user",
        string="PTKP Status",
        tracking=True,
        help="TK = Tidak Kawin, K = Kawin "
        "Sedangkan angka di belakangnya menunjukkan jumlah tanggungan",
    )
