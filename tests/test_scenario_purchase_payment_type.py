import datetime
import unittest
from decimal import Decimal

from proteus import Model
from trytond.modules.account.tests.tools import (create_chart,
                                                 create_fiscalyear, create_tax,
                                                 get_accounts)
from trytond.modules.account_invoice.tests.tools import (
    create_payment_term, set_fiscalyear_invoice_sequences)
from trytond.modules.company.tests.tools import create_company, get_company
from trytond.tests.test_tryton import drop_db
from trytond.tests.tools import activate_modules


class Test(unittest.TestCase):

    def setUp(self):
        drop_db()
        super().setUp()

    def tearDown(self):
        drop_db()
        super().tearDown()

    def test(self):

        # Install purchase_payment_type
        activate_modules('purchase_payment_type')

        # Create company
        _ = create_company()
        company = get_company()

        # Create fiscal year
        fiscalyear = set_fiscalyear_invoice_sequences(
            create_fiscalyear(company))
        fiscalyear.click('create_period')

        # Create chart of accounts
        _ = create_chart(company)
        accounts = get_accounts(company)
        revenue = accounts['revenue']
        expense = accounts['expense']

        # Create tax
        tax = create_tax(Decimal('.10'))
        tax.save()

        # Create account category
        ProductCategory = Model.get('product.category')
        account_category = ProductCategory(name="Account Category")
        account_category.accounting = True
        account_category.account_expense = expense
        account_category.account_revenue = revenue
        account_category.supplier_taxes.append(tax)
        account_category.save()

        # Create product
        ProductUom = Model.get('product.uom')
        unit, = ProductUom.find([('name', '=', 'Unit')])
        ProductTemplate = Model.get('product.template')
        template = ProductTemplate()
        template.name = 'product'
        template.default_uom = unit
        template.type = 'goods'
        template.purchasable = True
        template.list_price = Decimal('10')
        template.cost_price_method = 'fixed'
        template.account_category = account_category
        product, = template.products
        product.cost_price = Decimal('25')
        template.save()
        product, = template.products

        # Create payment term
        payment_term = create_payment_term()
        payment_term.save()

        # Create payment type
        PaymentType = Model.get('account.payment.type')
        receivable = PaymentType(name='Receivable', kind='receivable')
        receivable.save()
        payable = PaymentType(name='Payable', kind='payable')
        payable.save()

        # Create party
        Party = Model.get('party.party')
        party = Party(name='Party')
        party.customer_payment_type = receivable
        party.supplier_payment_type = payable
        party.save()

        # Purchase with payment type payable
        Purchase = Model.get('purchase.purchase')
        PurchaseLine = Model.get('purchase.line')
        purchase = Purchase()
        purchase.party = party
        purchase.payment_term = payment_term
        purchase.payment_type = payable
        purchase.invoice_method = 'order'
        purchase_line = PurchaseLine()
        purchase.lines.append(purchase_line)
        purchase_line.product = product
        purchase_line.quantity = 2.0
        purchase_line = PurchaseLine()
        purchase.lines.append(purchase_line)
        purchase_line.product = product
        purchase_line.quantity = 3.0
        purchase.click('quote')
        purchase.click('confirm')
        purchase.click('process')
        self.assertEqual(purchase.state, 'processing')
        invoice, = purchase.invoices
        self.assertEqual(invoice.payment_type, payable)

        # Purchase with payment type payable and negative untaxed amount
        purchase = Purchase()
        purchase.party = party
        purchase.payment_term = payment_term
        purchase.payment_type = payable
        purchase.invoice_method = 'order'
        purchase_line = PurchaseLine()
        purchase.lines.append(purchase_line)
        purchase_line.product = product
        purchase_line.quantity = -2.0
        purchase_line = PurchaseLine()
        purchase.lines.append(purchase_line)
        purchase_line.product = product
        purchase_line.quantity = -3.0
        purchase.click('quote')
        purchase.click('confirm')
        purchase.click('process')
        self.assertEqual(purchase.state, 'processing')
        invoice, = purchase.invoices
        self.assertEqual(invoice.payment_type, receivable)

        # Invoice more than purchased
        purchase = Purchase()
        purchase.party = party
        purchase.payment_term = payment_term
        purchase.payment_type = payable
        purchase.invoice_method = 'order'
        purchase_line = PurchaseLine()
        purchase.lines.append(purchase_line)
        purchase_line.product = product
        purchase_line.quantity = 2.0
        purchase.click('quote')
        purchase.click('confirm')
        purchase.click('process')
        self.assertEqual(purchase.state, 'processing')
        invoice, = purchase.invoices
        line, = invoice.lines
        line.quantity = 10.0
        line.save()
        invoice.reload()
        invoice.invoice_date = datetime.date.today()
        invoice.save()
        invoice.click('validate_invoice')
        invoice.click('post')
        purchase.reload()
        self.assertEqual(len(purchase.invoices), 2)
        invoice1, invoice2 = purchase.invoices
        self.assertGreater(invoice1.untaxed_amount, Decimal('0.0'))
        self.assertEqual(invoice1.payment_type, payable)
        self.assertLess(invoice2.untaxed_amount, Decimal('0.0'))
        self.assertEqual(invoice2.payment_type, receivable)
