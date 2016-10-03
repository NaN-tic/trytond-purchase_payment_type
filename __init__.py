# This file is part of purchase_payment_type module for Tryton.
# The COPYRIGHT file at the top level of this repository contains
# the full copyright notices and license terms.
from trytond.pool import Pool
from .purchase import *


def register():
    Pool.register(
        PaymentType,
        Purchase,
        module='purchase_payment_type', type_='model')
