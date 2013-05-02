#This file is part of purchase_payment_type module for Tryton.
#The COPYRIGHT file at the top level of this repository contains 
#the full copyright notices and license terms.

from trytond.model import fields
from trytond.pool import Pool, PoolMeta
from trytond.pyson import Eval

__all__ = ['Purchase']
__metaclass__ = PoolMeta


_STATES = {
    'readonly': Eval('state') != 'draft',
}
_DEPENDS = ['state']

class Purchase:
    'Purchase'
    __name__ = 'purchase.purchase'

    payment_type = fields.Many2One('account.payment.type',
        'Payment Type', states=_STATES, depends=_DEPENDS,
        domain=[('kind','=','payable')])

    @classmethod
    def default_payment_type(cls):
        PaymentType = Pool().get('account.payment.type')
        payment_types = PaymentType.search(cls.payment_type.domain)
        if len(payment_types) == 1:
            return payment_types[0].id

    def on_change_party(self):
        changes = super(Purchase, self).on_change_party()
        if self.party and self.party.customer_payment_type:
            changes['payment_type'] = self.party.customer_payment_type.id
        return changes

    def _get_invoice_purchase(self, invoice_type):
        invoice = super(Purchase, self)._get_invoice_purchase(invoice_type)
        if self.payment_type:
            invoice.payment_type = self.payment_type
        return invoice
