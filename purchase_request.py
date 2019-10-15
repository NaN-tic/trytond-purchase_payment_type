# The COPYRIGHT file at the top level of this repository contains
# the full copyright notices and license terms.
from trytond.model import fields
from trytond.pool import PoolMeta

__all__ = ['PurchaseRequest', 'CreatePurchase']


class PurchaseRequest(metaclass=PoolMeta):
    __name__ = 'purchase.request'
    payment_type = fields.Function(fields.Many2One('account.payment.type',
        'Payment Type'), 'get_payment_type')

    @classmethod
    def get_payment_type(cls, requests, name):
        res = dict((x.id, None) for x in requests)
        for req in requests:
            if req.party and req.party.supplier_payment_type:
                res[req.id] = req.party.supplier_payment_type
        return res


class CreatePurchase(metaclass=PoolMeta):
    __name__ = 'purchase.request.create_purchase'

    @classmethod
    def _group_purchase_key(cls, requests, request):
        key = super(CreatePurchase, cls)._group_purchase_key(requests, request)
        return key + (
            ('payment_type', request.payment_type),
            )
