# -*- coding: utf-8 -*-
# Copyright 2016 OpenSynergy Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp.tests.common import TransactionCase


class HrEmployeeCase(TransactionCase):

    def setUp(self, *args, **kwargs):
        super(HrEmployeeCase, self).setUp(*args, **kwargs)

        self.employee = self.env["hr.employee"].create({
            "name": "X Employee",
        })

        self.period1 = self.env.ref("l10n_id_taxform_period.period_2")
        self.period2 = self.env.ref("l10n_id_taxform_period.period_7")

    def test_1(self):

        contract = self.env["hr.contract"].create({
            "name": "X Contract",
            "employee_id": self.employee.id,
            "date_start": self.period1.date_start,
            "wage": 0.0,
            "type_id": self.env.ref("hr_contract.hr_contract_type_emp").id,
        })
        self.assertEqual(
            self.employee.joining_tax_period_id,
            self.period1,
        )
        self.assertEqual(
            self.employee.joining_tax_year_id,
            self.period1.year_id,
        )
        contract.write({
            "date_start": self.period2.date_start})
        self.assertEqual(
            self.employee.joining_tax_period_id,
            self.period2,
        )
        self.assertEqual(
            self.employee.joining_tax_year_id,
            self.period2.year_id,
        )
