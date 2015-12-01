# This file is part of the purchase_payment_type module for Tryton.
# The COPYRIGHT file at the top level of this repository contains the full
# copyright notices and license terms.
import unittest
import trytond.tests.test_tryton
from trytond.tests.test_tryton import ModuleTestCase


class PurchasePaymentTypeTestCase(ModuleTestCase):
    'Test Purchase Payment Type module'
    module = 'purchase_payment_type'


def suite():
    suite = trytond.tests.test_tryton.suite()
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(
        PurchasePaymentTypeTestCase))
    return suite