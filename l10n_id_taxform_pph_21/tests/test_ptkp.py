# Copyright 2016 OpenSynergy Indonesia
# Copyright 2021 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp.tests.common import TransactionCase


class PtkpCase(TransactionCase):
    def setUp(self, *args, **kwargs):
        super(PtkpCase, self).setUp(*args, **kwargs)
        self.cat_1 = self.env.ref("l10n_id_taxform_pph_21.ptkp_k0")
        self.cat_2 = self.env.ref("l10n_id_taxform_pph_21.ptkp_tk2")

    def test_1(self):
        self.assertEqual(self.cat_1.get_rate(), 58500000.0)

    def test_2(self):
        self.assertEqual(self.cat_2.get_rate(), 63000000.0)
