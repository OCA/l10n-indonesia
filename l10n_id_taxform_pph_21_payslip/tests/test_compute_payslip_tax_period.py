# -*- coding: utf-8 -*-
# Copyright 2017 OpenSynergy Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp.tests.common import TransactionCase
import time


class TestComputePayslipTaxPeriod(TransactionCase):

    def setUp(self, *args, **kwargs):
        super(TestComputePayslipTaxPeriod, self).setUp(*args, **kwargs)
        # Objects
        self.obj_hr_employee = self.env['hr.employee']
        self.obj_struct = self.env['hr.payroll.structure']
        self.obj_payslip = self.env['hr.payslip']
        self.obj_contract = self.env['hr.contract']

        # Data
        self.country = self.env.ref(
            'base.id')
        self.department = self.env.ref(
            'hr.dep_rd')
        self.company = self.env.ref('base.main_company')
        self.rule_1 = self.env.ref(
            'hr_payroll.hr_salary_rule_houserentallowance1')
        self.rule_2 = self.env.ref(
            'hr_payroll.hr_salary_rule_convanceallowance1')
        self.rule_3 = self.env.ref(
            'hr_payroll.hr_salary_rule_professionaltax1')
        self.rule_4 = self.env.ref(
            'hr_payroll.hr_salary_rule_providentfund1')
        self.rule_5 = self.env.ref(
            'hr_payroll.hr_salary_rule_meal_voucher')
        self.rule_6 = self.env.ref(
            'hr_payroll.hr_salary_rule_sales_commission')
        self.type =\
            self.env.ref('hr_contract.hr_contract_type_emp')
        self.resource =\
            self.env.ref('resource.timesheet_group1')
        self.employee = self._create_employee()
        self.struct = self._create_structure()
        self.contract = self._create_contract()

    def _create_employee(self):
        vals = {
            'name': 'Mike',
            'country_id': self.country.id,
            'department_id': self.department.id,
            'birthday': '1985-05-11',
            'gender': 'male'
        }

        employee = self.obj_hr_employee.create(vals)
        return employee

    def _create_structure(self):
        vals = {
            'name': 'Test Salary Structure',
            'code': 'TST',
            'company_id': self.company.id,
            'rule_ids': [(6, 0, [
                self.rule_1.id,
                self.rule_2.id,
                self.rule_3.id,
                self.rule_4.id,
                self.rule_5.id,
                self.rule_6.id
            ])]

        }

        struct = self.obj_struct.create(vals)
        return struct

    def _create_contract(self):
        vals = {
            'name': 'Test Contract',
            'date_start': time.strftime('%Y-%m')+'-1',
            'date_end': time.strftime('%Y')+'-12-31',
            'wage': 7500000.0,
            'type_id': self.type.id,
            'employee_id': self.employee.id,
            'struct_id': self.struct.id,
            'working_hours': self.resource.id
        }

        contract = self.obj_contract.create(vals)
        return contract

    def test_compute_payslip_tax_period(self):
        # Create Payslip
        vals = {
            'employee_id': self.employee.id,
            'contract_id': self.contract.id,
            'struct_id': self.struct.id
        }
        new = self.obj_payslip.create(vals)

        # Test 1
        self.assertNotEqual(1, new.joining_tax_month)

        # Test 2
        new.date_from = '2000-01-01'
        new.date_to = '2000-01-31'
        self.assertEqual(1, new.joining_tax_month)
