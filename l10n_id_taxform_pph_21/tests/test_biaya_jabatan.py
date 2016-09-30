# -*- coding: utf-8 -*-
# Copyright 2016 OpenSynergy Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp.tests.common import TransactionCase


class BiayaJabatanCase(TransactionCase):

    def setUp(self, *args, **kwargs):
        super(BiayaJabatanCase, self).setUp(*args, **kwargs)
        self.obj_biaya_jabatan = self.env["l10n_id.pph_21_biaya_jabatan"]
        self.penghasilan_rutin = 5000000.0
        self.penghasilan_non_rutin = 10000000.0

    def test_1(self):
        biaya_jabatan = self.obj_biaya_jabatan.find()
        result = biaya_jabatan.get_biaya_jabatan(
            jumlah_penghasilan=5000000.00,
            masa_kerja=1
        )
        self.assertEqual(
            result,
            250000.00
        )

    def test_2(self):
        biaya_jabatan = self.obj_biaya_jabatan.find()
        result = biaya_jabatan.get_biaya_jabatan(
            jumlah_penghasilan=60000000.0,
            masa_kerja=12
        )
        self.assertEqual(
            result,
            3000000.0,
        )

    def test_3(self):
        biaya_jabatan = self.obj_biaya_jabatan.find()
        result = biaya_jabatan.get_biaya_jabatan(
            jumlah_penghasilan=20000000.00,
            masa_kerja=1
        )
        self.assertEqual(
            result,
            500000.0
        )
