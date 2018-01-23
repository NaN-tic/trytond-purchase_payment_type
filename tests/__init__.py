# This file is part of purchase_payment_type module for Tryton.
# The COPYRIGHT file at the top level of this repository contains
# the full copyright notices and license terms.
try:
    from trytond.modules.purchase_payment_type.tests.test_purchase_payment_type import suite
except ImportError:
    from .test_purchase_payment_type import suite

__all__ = ['suite']
