# -*- coding: utf-8 -*-
# Copyright 2016 OpenSynergy Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp.tests.common import TransactionCase


class Pph21RateCase(TransactionCase):

    def setUp(self, *args, **kwargs):
        super(Pph21RateCase, self).setUp(*args, **kwargs)
        self.partner = self.env.ref("base.main_partner")
        self.ptkp_category = self.env.ref("l10n_id_taxform_pph_21.ptkp_k0")
        self.partner.write({"ptkp_category_id": self.ptkp_category.id})

    def test_1(self):
        self.partner.write({"vat": "123"})
        pph = self.partner.compute_pph_21_2110001(
            bulan_bergabung=1,
            gaji=5000000.0,
            jumlah_penghasilan_non_rutin=10000000.0,
            pensiun=100000.0,
        )
        self.assertEqual(
            pph["pengurang"],
            600000.0)
        self.assertEqual(
            pph["netto"],
            14400000.00)
        self.assertEqual(
            pph["netto_setahun"],
            65550000.0)
        self.assertEqual(
            pph["ptkp"],
            39000000.0)
        self.assertEqual(
            pph["pkp"],
            26550000.00)
        self.assertEqual(
            pph["pph_setahun"],
            1327500.0)
        self.assertEqual(
            pph["pph"],
            557500.0)

    def test_2(self):
        self.partner.write({"vat": "123"})
        pph = self.partner.compute_pph_21_2110001(
            bulan_bergabung=2,
            gaji=5000000.0,
            jumlah_penghasilan_non_rutin=10000000.0,
            pensiun=100000.0,
        )
        self.assertEqual(
            pph["pengurang"],
            600000.0)
        self.assertEqual(
            pph["netto"],
            14400000.00)
        self.assertEqual(
            pph["netto_setahun"],
            60900000.0)
        self.assertEqual(
            pph["ptkp"],
            39000000.0)
        self.assertEqual(
            pph["pkp"],
            21900000.00)
        self.assertEqual(
            pph["pph_setahun"],
            1095000.0)
        self.assertEqual(
            pph["pph"],
            542727.0)

    def test_3(self):
        self.partner.write({"vat": ""})
        pph = self.partner.compute_pph_21_2110001(
            bulan_bergabung=1,
            gaji=5000000.0,
            jumlah_penghasilan_non_rutin=10000000.0,
            pensiun=100000.0,
        )
        self.assertEqual(
            pph["pengurang"],
            600000.0)
        self.assertEqual(
            pph["netto"],
            14400000.00)
        self.assertEqual(
            pph["netto_setahun"],
            65550000.0)
        self.assertEqual(
            pph["ptkp"],
            39000000.0)
        self.assertEqual(
            pph["pkp"],
            26550000.00)
        self.assertEqual(
            pph["pph_setahun"],
            1327500.0)
        self.assertEqual(
            pph["pph"],
            669000.0)

    def test_4(self):
        self.partner.write({"vat": "123"})
        pph = self.partner.compute_pph_21_2110001(
            bulan_bergabung=1,
            jumlah_penghasilan_non_rutin=10000000.0,
        )
        self.assertEqual(
            pph["pengurang"],
            500000.0)
        self.assertEqual(
            pph["netto"],
            9500000.00)
        self.assertEqual(
            pph["netto_setahun"],
            9500000.0)
        self.assertEqual(
            pph["ptkp"],
            0.0)
        self.assertEqual(
            pph["pkp"],
            9500000.00)
        self.assertEqual(
            pph["pph_setahun"],
            475000.0)
        self.assertEqual(
            pph["pph"],
            475000.0)

    def test_5(self):
        self.partner.write({"vat": "123"})
        pph = self.partner.compute_pph_21_2110001(
            bulan_bergabung=1,
            gaji=5000000.0
        )
        self.assertEqual(
            pph["pengurang"],
            250000.0)
        self.assertEqual(
            pph["netto"],
            4750000.00)
        self.assertEqual(
            pph["netto_setahun"],
            57000000.0)
        self.assertEqual(
            pph["ptkp"],
            39000000)
        self.assertEqual(
            pph["pkp"],
            18000000.00)
        self.assertEqual(
            pph["pph_setahun"],
            900000.0)
        self.assertEqual(
            pph["pph"],
            75000.0)
