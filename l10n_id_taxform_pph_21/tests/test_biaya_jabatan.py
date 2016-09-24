# -*- coding: utf-8 -*-
# Copyright 2016 OpenSynergy Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp.tests.common import TransactionCase


class BiayaJabatanCase(TransactionCase):

    def setUp(self, *args, **kwargs):
        super(BiayaJabatanCase, self).setUp(*args, **kwargs)
        self.obj_biaya_jabatan = self.env["l10n_id.pph_21_biaya_jabatan"]

    def test_1(self):
        biaya_jabatan = self.obj_biaya_jabatan.find()
        result = biaya_jabatan.get_biaya_jabatan(
            5000000.00,
            10000000.00,
        )
        self.assertEqual(
            result["biaya_jabatan_rutin"],
            250000.00
        )
        self.assertEqual(
            result["biaya_jabatan_non_rutin"],
            250000.00
        )

    def test_2(self):
        biaya_jabatan = self.obj_biaya_jabatan.find()
        result = biaya_jabatan.get_biaya_jabatan(
            5000000.00,
            0.00,
        )
        self.assertEqual(
            result["biaya_jabatan_rutin"],
            250000.00
        )
        self.assertEqual(
            result["biaya_jabatan_non_rutin"],
            0.00
        )

    def test_3(self):
        biaya_jabatan = self.obj_biaya_jabatan.find()
        result = biaya_jabatan.get_biaya_jabatan(
            0.00,
            10000000.00
        )
        self.assertEqual(
            result["biaya_jabatan_rutin"],
            0.00,
        )
        self.assertEqual(
            result["biaya_jabatan_non_rutin"],
            500000.00
        )
