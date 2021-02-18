# Copyright 2016 OpenSynergy Indonesia
# Copyright 2021 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp.tests.common import TransactionCase


class Pph21RateCase(TransactionCase):
    def setUp(self, *args, **kwargs):
        super(Pph21RateCase, self).setUp(*args, **kwargs)
        self.partner = self.env.ref("base.main_partner")
        self.ptkp_category = self.env.ref("l10n_id_taxform_pph_21.ptkp_k2")
        self.partner.write({"ptkp_category_id": self.ptkp_category.id})

    def test_1(self):
        self.partner.write({"vat": ""})
        pph = self.partner.compute_pph_21_2110001(
            bulan_bergabung=1,
            tanggal_pemotongan="2021-1-30",
            gaji=6000000.0,
            jumlah_penghasilan_non_rutin=10000000.0,
            tunjangan_pph=0.0,
            tunjangan_lain=0.0,
            pensiun=120000.0,
            akumulasi_penghasilan_non_rutin=0.0,
            akumulasi_pensiun=0.0,
            akumulasi_tunjangan_lain=0.0,
            akumulasi_tunjangan_pph=0.0,
            akumulasi_gaji=0.0,
            akumulasi_pph_yang_disetor=0.0,
            is_keluar=False,
            is_lokal=True,
        )

        self.assertEqual(pph["jumlah_penghasilan_rutin"], 6000000.0)
        self.assertEqual(pph["jumlah_penghasilan_rutin_setahun"], 72000000.0)
        self.assertEqual(pph["jumlah_penghasilan_non_rutin"], 10000000.0)
        self.assertEqual(pph["biaya_jabatan"], 500000.0)
        self.assertEqual(pph["biaya_jabatan_rutin_setahun"], 3600000.0)
        self.assertEqual(pph["biaya_jabatan_non_rutin_setahun"], 500000.0)
        self.assertEqual(pph["biaya_jabatan_setahun"], 4100000.0)
        self.assertEqual(pph["netto_setahun"], 76460000.0)
        self.assertEqual(pph["ptkp"], 67500000.0)
        self.assertEqual(pph["pkp"], 8960000.00)
        self.assertEqual(pph["pph_setahun"], 537600.0)
        self.assertEqual(pph["pph_setahun_rutin"], 0.0)
        self.assertEqual(pph["pph_non_rutin"], 537600.0)
        self.assertEqual(pph["pph"], 537600.0)

    def test_2(self):
        self.partner.write({"vat": ""})
        pph = self.partner.compute_pph_21_2110001(
            bulan_bergabung=4,
            tanggal_pemotongan="2021-4-30",
            gaji=6000000.0,
            jumlah_penghasilan_non_rutin=10000000.0,
            tunjangan_pph=0.0,
            tunjangan_lain=0.0,
            pensiun=120000.0,
            akumulasi_penghasilan_non_rutin=0.0,
            akumulasi_pensiun=0.0,
            akumulasi_tunjangan_lain=0.0,
            akumulasi_tunjangan_pph=0.0,
            akumulasi_gaji=0.0,
            akumulasi_pph_yang_disetor=0.0,
            is_keluar=False,
            is_lokal=True,
        )

        self.assertEqual(pph["jumlah_penghasilan_rutin"], 6000000.0)
        self.assertEqual(pph["jumlah_penghasilan_rutin_setahun"], 54000000.0)
        self.assertEqual(pph["jumlah_penghasilan_non_rutin"], 10000000.0)
        self.assertEqual(pph["biaya_jabatan"], 500000.0)
        self.assertEqual(pph["biaya_jabatan_rutin_setahun"], 2700000.0)
        self.assertEqual(pph["biaya_jabatan_non_rutin_setahun"], 500000.0)
        self.assertEqual(pph["biaya_jabatan_setahun"], 3200000.0)
        self.assertEqual(pph["netto_setahun"], 59720000.0)
        self.assertEqual(pph["ptkp"], 67500000.0)
        self.assertEqual(pph["pkp"], 0.00)
        self.assertEqual(pph["pph_setahun"], 0.0)
        self.assertEqual(pph["pph_setahun_rutin"], 0.0)
        self.assertEqual(pph["pph_non_rutin"], 0.0)
        self.assertEqual(pph["pph"], 0.0)

    def test_3(self):
        self.partner.write({"vat": ""})
        pph = self.partner.compute_pph_21_2110001(
            bulan_bergabung=4,
            tanggal_pemotongan="2021-4-30",
            gaji=6000000.0,
            jumlah_penghasilan_non_rutin=10000000.0,
            tunjangan_pph=0.0,
            tunjangan_lain=0.0,
            pensiun=120000.0,
            akumulasi_penghasilan_non_rutin=0.0,
            akumulasi_pensiun=0.0,
            akumulasi_tunjangan_lain=0.0,
            akumulasi_tunjangan_pph=0.0,
            akumulasi_gaji=0.0,
            akumulasi_pph_yang_disetor=0.0,
            is_keluar=False,
            is_lokal=False,
        )

        self.assertEqual(pph["jumlah_penghasilan_rutin"], 6000000.0)
        self.assertEqual(pph["jumlah_penghasilan_rutin_setahun"], 72000000.0)
        self.assertEqual(pph["jumlah_penghasilan_non_rutin"], 10000000.0)
        self.assertEqual(pph["biaya_jabatan"], 500000.0)
        self.assertEqual(pph["biaya_jabatan_rutin_setahun"], 3600000.0)
        self.assertEqual(pph["biaya_jabatan_non_rutin_setahun"], 500000.0)
        self.assertEqual(pph["biaya_jabatan_setahun"], 4100000.0)
        self.assertEqual(pph["netto_setahun"], 76460000.0)
        self.assertEqual(pph["ptkp"], 67500000.0)
        self.assertEqual(pph["pkp"], 8960000.0)
        self.assertEqual(pph["pph_setahun"], 537600.0)
        self.assertEqual(pph["pph_setahun_rutin"], 0.0)
        self.assertEqual(pph["pph_non_rutin"], 537600.0)
        self.assertEqual(pph["pph"], 537600.0)

    def test_4(self):
        self.partner.write({"vat": ""})
        pph = self.partner.compute_pph_21_2110001(
            bulan_bergabung=1,
            tanggal_pemotongan="2021-1-30",
            gaji=8000000.0,
            jumlah_penghasilan_non_rutin=00.0,
            tunjangan_pph=0.0,
            tunjangan_lain=0.0,
            pensiun=0.0,
            akumulasi_penghasilan_non_rutin=0.0,
            akumulasi_pensiun=0.0,
            akumulasi_tunjangan_lain=0.0,
            akumulasi_tunjangan_pph=0.0,
            akumulasi_gaji=0.0,
            akumulasi_pph_yang_disetor=0.0,
            is_keluar=False,
            is_lokal=False,
        )

        self.assertEqual(pph["jumlah_penghasilan_rutin"], 8000000.0)
        self.assertEqual(pph["jumlah_penghasilan_rutin_setahun"], 96000000.0)
        self.assertEqual(pph["jumlah_penghasilan_non_rutin"], 0.0)
        self.assertEqual(pph["biaya_jabatan"], 400000.0)
        self.assertEqual(pph["biaya_jabatan_rutin_setahun"], 4800000.0)
        self.assertEqual(pph["biaya_jabatan_non_rutin_setahun"], 0.0)
        self.assertEqual(pph["biaya_jabatan_setahun"], 4800000.0)
        self.assertEqual(pph["netto_setahun"], 91200000.0)
        self.assertEqual(pph["ptkp"], 67500000.0)
        self.assertEqual(pph["pkp"], 23700000.0)
        self.assertEqual(pph["pph_setahun"], 1422000.0)
        self.assertEqual(pph["pph_setahun_rutin"], 1422000.0)
        self.assertEqual(pph["pph_non_rutin"], 0.0)
        self.assertEqual(pph["pph"], 118500.0)

    def test_5(self):
        self.partner.write({"vat": ""})
        pph = self.partner.compute_pph_21_2110001(
            bulan_bergabung=1,
            tanggal_pemotongan="2021-1-30",
            gaji=8000000.0,
            jumlah_penghasilan_non_rutin=5000000.0,
            tunjangan_pph=0.0,
            tunjangan_lain=0.0,
            pensiun=0.0,
            akumulasi_penghasilan_non_rutin=0.0,
            akumulasi_pensiun=0.0,
            akumulasi_tunjangan_lain=0.0,
            akumulasi_tunjangan_pph=0.0,
            akumulasi_gaji=0.0,
            akumulasi_pph_yang_disetor=0.0,
            is_keluar=False,
            is_lokal=False,
        )

        self.assertEqual(pph["jumlah_penghasilan_rutin"], 8000000.0)
        self.assertEqual(pph["jumlah_penghasilan_rutin_setahun"], 96000000.0)
        self.assertEqual(pph["jumlah_penghasilan_non_rutin"], 5000000.0)
        self.assertEqual(pph["biaya_jabatan"], 500000.0)
        self.assertEqual(pph["biaya_jabatan_rutin_setahun"], 4800000.0)
        self.assertEqual(pph["biaya_jabatan_non_rutin_setahun"], 250000.0)
        self.assertEqual(pph["biaya_jabatan_setahun"], 5050000.0)
        self.assertEqual(pph["netto_setahun"], 95950000.0)
        self.assertEqual(pph["ptkp"], 67500000.0)
        self.assertEqual(pph["pkp"], 28450000.0)
        self.assertEqual(pph["pph_setahun"], 1707000.0)
        self.assertEqual(pph["pph_setahun_rutin"], 1422000.0)
        self.assertEqual(pph["pph_non_rutin"], 285000.0)
        self.assertEqual(pph["pph"], 403500.0)

    def test_6(self):
        self.partner.write({"vat": ""})
        pph = self.partner.compute_pph_21_2110001(
            bulan_bergabung=1,
            tanggal_pemotongan="2021-12-30",
            gaji=8000000.0,
            jumlah_penghasilan_non_rutin=0.0,
            tunjangan_pph=0.0,
            tunjangan_lain=0.0,
            pensiun=0.0,
            akumulasi_penghasilan_non_rutin=5000000.0,
            akumulasi_pensiun=0.0,
            akumulasi_tunjangan_lain=0.0,
            akumulasi_tunjangan_pph=0.0,
            akumulasi_gaji=88000000,
            akumulasi_pph_yang_disetor=1303500.0,
            is_keluar=False,
            is_lokal=True,
        )

        self.assertEqual(pph["jumlah_penghasilan_rutin"], 96000000.0)
        self.assertEqual(pph["jumlah_penghasilan_rutin_setahun"], 96000000.0)
        self.assertEqual(pph["jumlah_penghasilan_non_rutin"], 5000000.0)
        self.assertEqual(pph["biaya_jabatan"], 5050000.0)
        self.assertEqual(pph["biaya_jabatan_rutin_setahun"], 4800000.0)
        self.assertEqual(pph["biaya_jabatan_non_rutin_setahun"], 250000.0)
        self.assertEqual(pph["biaya_jabatan_setahun"], 5050000.0)
        self.assertEqual(pph["netto_setahun"], 95950000.0)
        self.assertEqual(pph["ptkp"], 67500000.0)
        self.assertEqual(pph["pkp"], 28450000.0)
        self.assertEqual(pph["pph_setahun"], 1707000.0)
        self.assertEqual(pph["pph_setahun_rutin"], 1422000.0)
        self.assertEqual(pph["pph_non_rutin"], 285000.0)
        self.assertEqual(pph["pph"], 403500.0)
