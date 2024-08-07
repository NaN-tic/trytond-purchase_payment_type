import datetime
import unittest
from decimal import Decimal

from proteus import Model, Wizard
from trytond.modules.account.tests.tools import (create_chart, create_tax,
                                                 get_accounts)
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

        # Install stock_supply and purchase_payment_type Module
        activate_modules(
            ['purchase_request', 'stock_supply', 'purchase_payment_type'])

        # Create company
        _ = create_company()
        company = get_company()

        # Create chart of accounts
        _ = create_chart(company)
        accounts = get_accounts(company)
        expense = accounts['expense']
        revenue = accounts['revenue']

        # Create tax
        tax = create_tax(Decimal('.10'))
        tax.save()

        # Create payment type
        PaymentType = Model.get('account.payment.type')
        receivable = PaymentType(name='Receivable', kind='receivable')
        receivable.save()
        payable = PaymentType(name='Payable', kind='payable')
        payable.save()

        # Create parties
        Party = Model.get('party.party')
        customer = Party(name='Customer')
        customer.save()
        supplier = Party(name='Supplier')
        supplier.customer_payment_type = receivable
        supplier.supplier_payment_type = payable
        supplier.save()

        # Create account category
        ProductCategory = Model.get('product.category')
        account_category = ProductCategory(name="Account Category")
        account_category.accounting = True
        account_category.account_expense = expense
        account_category.account_revenue = revenue
        account_category.save()
        account_category_tax, = account_category.duplicate()
        account_category_tax.supplier_taxes.append(tax)
        account_category_tax.save()

        # Create product
        ProductUom = Model.get('product.uom')
        ProductTemplate = Model.get('product.template')
        unit, = ProductUom.find([('name', '=', 'Unit')])
        template = ProductTemplate()
        template.name = 'Product'
        template.default_uom = unit
        template.type = 'goods'
        template.list_price = Decimal('20')
        template.purchasable = True
        template.account_category = account_category_tax
        product, = template.products
        product.cost_price = Decimal('8')
        template.save()
        product, = template.products

        # Get stock locations
        Location = Model.get('stock.location')
        warehouse_loc, = Location.find([('code', '=', 'WH')])
        supplier_loc, = Location.find([('code', '=', 'SUP')])
        customer_loc, = Location.find([('code', '=', 'CUS')])
        output_loc, = Location.find([('code', '=', 'OUT')])
        storage_loc, = Location.find([('code', '=', 'STO')])

        # Create a need for missing product
        today = datetime.date.today()
        ShipmentOut = Model.get('stock.shipment.out')
        shipment_out = ShipmentOut()
        shipment_out.planned_date = today
        shipment_out.effective_date = today
        shipment_out.customer = customer
        shipment_out.warehouse = warehouse_loc
        shipment_out.company = company
        move = shipment_out.outgoing_moves.new()
        move.product = product
        move.unit = unit
        move.quantity = 1
        move.from_location = output_loc
        move.to_location = customer_loc
        move.company = company
        move.unit_price = Decimal('1')
        move.currency = company.currency
        shipment_out.click('wait')

        # There is no purchase request
        PurchaseRequest = Model.get('purchase.request')
        self.assertEqual(PurchaseRequest.find([]), [])

        # Create the purchase request
        create_pr = Wizard('stock.supply')
        create_pr.execute('create_')

        # There is now a draft purchase request
        pr, = PurchaseRequest.find([('state', '=', 'draft')])
        self.assertEqual(pr.product, product)
        self.assertEqual(pr.quantity, 1.0)

        # Create the purchase then cancel it
        create_purchase = Wizard('purchase.request.create_purchase', [pr])
        create_purchase.form.party = supplier
        create_purchase.execute('start')
        self.assertEqual(pr.state, 'purchased')
        Purchase = Model.get('purchase.purchase')
        purchase, = Purchase.find()
        self.assertEqual(purchase.payment_type,
                         purchase.party.supplier_payment_type)
