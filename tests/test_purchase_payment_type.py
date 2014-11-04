#!/usr/bin/env python
# -*- coding: UTF-8 -*-
# This file is part of purchase_payment_type module for Tryton.
# The COPYRIGHT file at the top level of this repository contains
# the full copyright notices and license terms.
import unittest
import trytond.tests.test_tryton
from trytond.tests.test_tryton import test_view, test_depends


class PurchasePaymentTypeTestCase(unittest.TestCase):
    'Test PurchasePaymentType module'

    def setUp(self):
        trytond.tests.test_tryton.install_module('purchase_payment_type')

    def test0005views(self):
        'Test views'
        test_view('purchase_payment_type')

    def test0006depends(self):
        'Test depends'
        test_depends()


def suite():
    suite = trytond.tests.test_tryton.suite()
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(
        PurchasePaymentTypeTestCase))
    return suite
