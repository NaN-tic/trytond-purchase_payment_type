Purchase Payment Type Module
############################

The purchase_payment_type tryton module adds payment type to purchase process.
The purchase order inherits payment type from party as default. Then, the
invoice based on this purchase order inherits the payment information from it.
Also computes payment type of invoices created from picking lists (extracted
from party info).
