# Copyright 2016 OpenSynergy Indonesia
# Copyright 2021 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp.tests.common import TransactionCase


class BiayaJabatanCase(TransactionCase):
    def setUp(self, *args, **kwargs):
        super(BiayaJabatanCase, self).setUp(*args, **kwargs)
        self.obj_biaya_jabatan = self.env["l10n_id.pph_21_biaya_jabatan"]

    # Test biaya jabatan dibawah max biaya jabatan)
    def test_1(self):
        biaya_jabatan = self.obj_biaya_jabatan.find()
        result = biaya_jabatan.get_biaya_jabatan(
            jumlah_penghasilan_rutin=5000000,
            jumlah_penghasilan_rutin_setahun=5000000 * 12,
            jumlah_penghasilan_non_rutin=2000000,
            is_keluar=False,
        )
        self.assertEqual(result["biaya_jabatan_rutin_setahun"], 3000000.00)
        self.assertEqual(result["biaya_jabatan_non_rutin_setahun"], 100000.00)
        self.assertEqual(result["biaya_jabatan_setahun"], 3100000.00)
        self.assertEqual(result["biaya_jabatan"], 350000.00)

    def test_2(self):
        biaya_jabatan = self.obj_biaya_jabatan.find()
        result = biaya_jabatan.get_biaya_jabatan(
            jumlah_penghasilan_rutin=5000000,
            jumlah_penghasilan_rutin_setahun=5000000 * 12,
            jumlah_penghasilan_non_rutin=10000000,
            is_keluar=False,
        )
        self.assertEqual(result["biaya_jabatan_rutin_setahun"], 3000000.00)
        self.assertEqual(result["biaya_jabatan_non_rutin_setahun"], 500000.00)
        self.assertEqual(result["biaya_jabatan_setahun"], 3500000.00)
        self.assertEqual(result["biaya_jabatan"], 500000.00)

    # Test biaya jabatan melebihi max biaya jabatan)
    def test_3(self):
        biaya_jabatan = self.obj_biaya_jabatan.find()
        result = biaya_jabatan.get_biaya_jabatan(
            jumlah_penghasilan_rutin=10000000,
            jumlah_penghasilan_rutin_setahun=10000000 * 12,
            jumlah_penghasilan_non_rutin=10000000,
            is_keluar=False,
        )
        self.assertEqual(result["biaya_jabatan_rutin_setahun"], 6000000.00)
        self.assertEqual(result["biaya_jabatan_non_rutin_setahun"], 0.00)
        self.assertEqual(result["biaya_jabatan_setahun"], 6000000.00)
        self.assertEqual(result["biaya_jabatan"], 500000.00)

    def test_4(self):
        biaya_jabatan = self.obj_biaya_jabatan.find()
        result = biaya_jabatan.get_biaya_jabatan(
            jumlah_penghasilan_rutin=10000000 * 12,
            jumlah_penghasilan_rutin_setahun=10000000 * 12,
            jumlah_penghasilan_non_rutin=10000000,
            is_keluar=True,
        )
        self.assertEqual(result["biaya_jabatan_rutin_setahun"], 6000000.00)
        self.assertEqual(result["biaya_jabatan_non_rutin_setahun"], 0.00)
        self.assertEqual(result["biaya_jabatan_setahun"], 6000000.00)
        self.assertEqual(result["biaya_jabatan"], 6000000.00)
