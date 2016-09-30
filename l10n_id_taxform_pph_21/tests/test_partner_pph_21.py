# -*- coding: utf-8 -*-
# Copyright 2016 OpenSynergy Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp.tests.common import TransactionCase


class Pph21RateCase(TransactionCase):

    def setUp(self, *args, **kwargs):
        super(Pph21RateCase, self).setUp(*args, **kwargs)
        self.partner = self.env.ref("base.main_partner")
        self.indonesia = self.env.ref("base.id")
        self.ptkp_category = self.env.ref("l10n_id_taxform_pph_21.ptkp_k0")
        self.partner.write({"ptkp_category_id": self.ptkp_category.id})

    def test_1(self):
        self.partner.write({"vat": "123", "nationality_id": self.indonesia.id})
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
        self.partner.write({"vat": "123", "nationality_id": self.indonesia.id})
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
        self.partner.write({"vat": "", "nationality_id": self.indonesia.id})
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
        self.partner.write({"vat": "123", "nationality_id": self.indonesia.id})
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
        self.partner.write({"vat": "123", "nationality_id": self.indonesia.id})
        pph = self.partner.compute_pph_21_2110001(
            bulan_bergabung=1,
            gaji=10000000.0
        )
        self.assertEqual(
            pph["pengurang"],
            500000.0)
        self.assertEqual(
            pph["netto"],
            9500000.0)
        self.assertEqual(
            pph["netto_setahun"],
            114000000.0)
        self.assertEqual(
            pph["ptkp"],
            39000000)
        self.assertEqual(
            pph["pkp"],
            75000000.00)
        self.assertEqual(
            pph["pph_setahun"],
            6250000.0)
        self.assertEqual(
            pph["pph"],
            520833.0)

    def test_6(self):
        self.partner.write({"vat": "123", "nationality_id": False})
        pph = self.partner.compute_pph_21_2110001(
            bulan_bergabung=1,
            gaji=10000000.0
        )
        self.assertEqual(
            pph["pengurang"],
            500000.0)
        self.assertEqual(
            pph["netto"],
            9500000.0)
        self.assertEqual(
            pph["netto_setahun"],
            114000000.0)
        self.assertEqual(
            pph["ptkp"],
            39000000)
        self.assertEqual(
            pph["pkp"],
            75000000.00)
        self.assertEqual(
            pph["pph_setahun"],
            6250000.0)
        self.assertEqual(
            pph["pph"],
            520833.0)

    def test_7(self):
        self.partner.write({"vat": "123", "nationality_id": self.indonesia.id})
        pph = self.partner.compute_pph_21_2110001(
            bulan_bergabung=3,
            gaji=10000000.0
        )
        self.assertEqual(
            pph["pengurang"],
            500000.0)
        self.assertEqual(
            pph["netto"],
            9500000.0)
        self.assertEqual(
            pph["netto_setahun"],
            95000000.0)
        self.assertEqual(
            pph["ptkp"],
            39000000)
        self.assertEqual(
            pph["pkp"],
            56000000.00)
        self.assertEqual(
            pph["pph_setahun"],
            3400000.0)
        self.assertEqual(
            pph["pph"],
            340000.0)

    def test_8(self):
        self.partner.write({"vat": "123", "nationality_id": False})
        pph = self.partner.compute_pph_21_2110001(
            bulan_bergabung=3,
            gaji=10000000.0
        )
        self.assertEqual(
            pph["pengurang"],
            500000.0)
        self.assertEqual(
            pph["netto"],
            9500000.0)
        self.assertEqual(
            pph["netto_setahun"],
            114000000.0)
        self.assertEqual(
            pph["ptkp"],
            39000000)
        self.assertEqual(
            pph["pkp"],
            75000000.00)
        self.assertEqual(
            pph["pph_setahun"],
            6250000.0)
        self.assertEqual(
            pph["pph"],
            520833.0)

    def test_9(self):
        self.partner.write({"vat": "123", "nationality_id": self.indonesia.id})
        pph = self.partner.compute_pph_21_2110001(
            bulan_bergabung=1,
            bulan_akhir=6,
            gaji=10000000.0,
            tunjangan_lain=40000.0,
            pensiun=200000,
            akumulasi_penghasilan=50200000.0,
            akumulasi_pensiun=1000000.0,
            pph_21_sudah_dipotong=2484167.0,
        )
        self.assertEqual(
            pph["pph"],
            -1632167.0)

    def test_10(self):
        self.partner.write({"vat": "123", "nationality_id": self.indonesia.id})
        pph = self.partner.compute_pph_21_2110001(
            bulan_bergabung=1,
            bulan_akhir=12,
            gaji=10000000.0,
            tunjangan_lain=40000.0,
            pensiun=200000,
            akumulasi_penghasilan=110440000.0,
            akumulasi_pensiun=2200000.0,
            pph_21_sudah_dipotong=5465167.0,
        )
        self.assertEqual(
            pph["pph"],
            496833.0)
