# -*- coding: utf-8 -*-
# © 2016  Denis Roussel, Acsone SA/NV (http://www.acsone.eu)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import openerp.tests.common as common


class TestStockPackagingSerial(common.TransactionCase):

    def setUp(self):
        super(TestStockPackagingSerial, self).setUp()
        gs1_obj = self.env['gs1_barcode']
        seq_obj = self.env['ir.sequence']

        seq = seq_obj.create({'name': 'test sequence',
                              'implementation': 'no_gap',
                              })

        ai = gs1_obj.search([('ai', '=', '00')])
        product_ul_obj = self.env['product.ul']
        self.ul_1 = product_ul_obj.create({'name': 'Pack Test',
                                           'type': 'box',
                                           'weight': 25.50,
                                           'gs1_barcode_id': ai[0].id,
                                           'package_sequence_id': seq.id})

    def test_serial_01(self):
        pack_obj = self.env['stock.quant.package']

        pack_1 = pack_obj.create({'name': 'PACK001',
                                  'ul_id': self.ul_1.id})

        self.assertEqual(False, not pack_1.serial_id)

        self.assertEqual('1', pack_1.serial_id.name)
