# -*- coding: utf-8 -*-
# Copyright 2016 OpenSynergy Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp.tests.common import TransactionCase
from datetime import datetime
from dateutil import relativedelta


class TaxPeriodCase(TransactionCase):

    def setUp(self, *args, **kwargs):
        super(TaxPeriodCase, self).setUp(*args, **kwargs)

        self.obj_period = self.env["l10n_id.tax_period"]
        self.obj_year = self.env["l10n_id.tax_year"]
        self.demo_year = self.env.ref("l10n_id_taxform_period.data_tax_year")

    def test_create_year(self):
        next_year = datetime.strptime(
            self.demo_year.date_start, "%Y-%m-%d").year + 1
        date_start_year = datetime(next_year, 1, 1)
        date_end_year = datetime(next_year, 12, 31)
        date_end_period = datetime(next_year, 1, 31)
        # User create Tax Year
        tax_year = self.obj_year.create({
            "name": str(next_year),
            "code": str(next_year),
            "date_start": date_start_year.strftime(
                "%Y-%m-%d"),
            "date_end": date_end_year.strftime(
                "%Y-%m-%d"),
        })
        # User create tax period
        tax_year.action_create_period()
        # Assert date_start and date_end periods that created
        for month in range(0, 12):
            self.assertEqual(
                tax_year.period_ids[month].date_start,
                (date_start_year +
                 relativedelta.relativedelta(
                     months=+month)).strftime("%Y-%m-%d"))
            self.assertEqual(
                tax_year.period_ids[month].date_end,
                (date_end_period +
                 relativedelta.relativedelta(
                     months=+month)).strftime("%Y-%m-%d"))
        # Check l10n_id.tax_year _find method
        self.assertEqual(
            self.obj_year._find_year(
                date_start_year.strftime("%Y-%m-%d")),
            tax_year)
        # Check l1on_id.tax_period _find method
        self.assertEqual(
            self.obj_period._find_period(
                date_start_year.strftime("%Y-%m-%d")),
            tax_year.period_ids[0])
        # Check forward find l1on_id.tax_period _find method
        self.assertEqual(
            tax_year.period_ids[1]._next_period(1),
            tax_year.period_ids[2])
        # Check backward find l1on_id.tax_period _find method
        self.assertEqual(
            tax_year.period_ids[2]._previous_period(1),
            tax_year.period_ids[1])
