# This file is part of purchase_payment_type module for Tryton.
# The COPYRIGHT file at the top level of this repository contains
# the full copyright notices and license terms.
from trytond.pool import Pool
from . import purchase
from . import purchase_request


def register():
    Pool.register(
        purchase.PaymentType,
        purchase.Purchase,
        module='purchase_payment_type', type_='model')
    Pool.register(
        purchase_request.PurchaseRequest,
        depends=['purchase_request'],
        module='purchase_payment_type', type_='model')
    Pool.register(
        purchase_request.CreatePurchase,
        depends=['purchase_request'],
        module='purchase_payment_type', type_='wizard')
