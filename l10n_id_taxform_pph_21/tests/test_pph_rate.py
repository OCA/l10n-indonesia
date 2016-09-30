# -*- coding: utf-8 -*-
# Copyright 2016 OpenSynergy Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp.tests.common import TransactionCase


class Pph21RateCase(TransactionCase):

    def setUp(self, *args, **kwargs):
        super(Pph21RateCase, self).setUp(*args, **kwargs)
        self.obj_pph_rate = self.env["l10n_id.pph_21_rate"]

    def test_1(self):
        pph_rate = self.obj_pph_rate.find()
        self.assertEqual(
            pph_rate.compute_tax(
                18000000.0),
            900000.0)

        self.assertEqual(
            pph_rate.compute_tax(
                46500000.0),
            2325000.0)
