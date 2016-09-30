# -*- coding: utf-8 -*-
# Copyright 2016 OpenSynergy Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp.tests.common import TransactionCase


class HrPayslipCase(TransactionCase):

    def setUp(self, *args, **kwargs):
        super(HrPayslipCase, self).setUp(*args, **kwargs)

        self.obj_partner = self.env["res.partner"]
        self.obj_employee = self.env["hr.employee"]
        self.obj_contract = self.env["hr.contract"]
        self.obj_payslip = self.env["hr.payslip"]
        self.obj_rule = self.env["hr.salary.rule"]
        self.obj_line = self.env["hr.payslip.line"]

        self.categ_pensiun = self.env.ref(
            "l10n_id_taxform_pph_21_payslip.rule_categ_pensiun")

        self.categ_pph = self.env.ref(
            "l10n_id_taxform_pph_21_payslip.rule_categ_pph")
        self.indonesia = self.env.ref(
            "base.id")

        # self.rule_pensiun = self.obj_rule.create({
        #     "name": "Pensiun",
        #     "code": "PEN",
        #     "categ_id": self.categ_pensiun.id,
        #     "sequence": 10,
        #     "condition_select": "none",
        #     "amount_select": "fix",
        #     "amount_fix": 0.0,
        #     })

        self.ptkp_categ_1 = self.env.ref(
            "l10n_id_taxform_pph_21.ptkp_k0")
        self.struct_1 = self.env.ref(
            "l10n_id_taxform_pph_21_payslip.payroll_structure_pph_1")
        self.period1 = self.env.ref(
            "l10n_id_taxform_period.period_1")
        self.period2 = self.env.ref(
            "l10n_id_taxform_period.period_2")
        self.period3 = self.env.ref(
            "l10n_id_taxform_period.period_3")
        self.period4 = self.env.ref(
            "l10n_id_taxform_period.period_4")
        self.period5 = self.env.ref(
            "l10n_id_taxform_period.period_5")
        self.period6 = self.env.ref(
            "l10n_id_taxform_period.period_6")
        self.period7 = self.env.ref(
            "l10n_id_taxform_period.period_7")
        self.period8 = self.env.ref(
            "l10n_id_taxform_period.period_8")
        self.period9 = self.env.ref(
            "l10n_id_taxform_period.period_9")
        self.period10 = self.env.ref(
            "l10n_id_taxform_period.period_10")
        self.period11 = self.env.ref(
            "l10n_id_taxform_period.period_11")
        self.period12 = self.env.ref(
            "l10n_id_taxform_period.period_12")

    def _create_test_payslip(
            self,
            contract,
            period,
            pph,
            test=True,
    ):
        payslip = self.obj_payslip.create({
            "employee_id": contract.employee_id.id,
            "contract_id": contract.id,
            "struct_id": contract.struct_id.id,
            "date_from": period.date_start,
            "date_to": period.date_end,
        })
        payslip.compute_sheet()
        criteria = [
            ("slip_id", "=", payslip.id),
            ("salary_rule_id.category_id.id", "=", self.categ_pph.id),
        ]
        line = self.obj_line.search(
            criteria,
            limit=1)
        if test:
            self.assertEqual(
                line.total,
                pph)
        payslip.process_sheet()
        return payslip

    def test_1(self):
        partner = self.obj_partner.create({
            "name": "X Partner 1",
            "vat": "7777777",
            "ptkp_category_id": self.ptkp_categ_1.id,
            "nationality_id": self.indonesia.id,
        })
        employee = self.obj_employee.create({
            "name": "X Employee 1",
            "address_home_id": partner.id,
        })
        contract = self.obj_contract.create({
            "name": "X Contract 1",
            "employee_id": employee.id,
            "date_start": self.period1.date_start,
            "date_end": False,
            "struct_id": self.struct_1.id,
            "wage": 10000000.0,
        })
        self._create_test_payslip(contract, self.period1, -520833.0)
        self._create_test_payslip(contract, self.period2, -520833.0)
        self._create_test_payslip(contract, self.period3, -520833.0)
        self._create_test_payslip(contract, self.period4, -520833.0)
        self._create_test_payslip(contract, self.period5, -520833.0)
        self._create_test_payslip(contract, self.period6, -520833.0)
        self._create_test_payslip(contract, self.period7, -520833.0)
        self._create_test_payslip(contract, self.period8, -520833.0)
        self._create_test_payslip(contract, self.period9, -520833.0)
        self._create_test_payslip(contract, self.period10, -520833.0)
        self._create_test_payslip(contract, self.period11, -520833.0)
        self._create_test_payslip(contract, self.period12, -520833.0)

    def test_2(self):
        partner = self.obj_partner.create({
            "name": "X Partner 1",
            "vat": "7777777",
            "ptkp_category_id": self.ptkp_categ_1.id,
            "nationality_id": self.indonesia.id,
        })
        employee = self.obj_employee.create({
            "name": "X Employee 1",
            "address_home_id": partner.id,
        })
        contract = self.obj_contract.create({
            "name": "X Contract 1",
            "employee_id": employee.id,
            "date_start": self.period1.date_start,
            "date_end": False,
            "struct_id": self.struct_1.id,
            "wage": 10000000.0,
        })
        self._create_test_payslip(contract, self.period1, -520833.0)
        self._create_test_payslip(contract, self.period2, -520833.0)
        self._create_test_payslip(contract, self.period3, -520833.0)
        self._create_test_payslip(contract, self.period4, -520833.0)
        self._create_test_payslip(contract, self.period5, -520833.0)
        contract.write({"date_end": self.period6.date_end})
        self._create_test_payslip(contract, self.period6, 1704165.0)
