# -*- coding: utf-8 -*-
# © 2016  Denis Roussel, Acsone SA/NV (http://www.acsone.eu)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import openerp.tests.common as common


class TestStockPackagingSerialSSCC(common.TransactionCase):

    def setUp(self):
        super(TestStockPackagingSerialSSCC, self).setUp()
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

        self.company = self.env.ref('base.main_company')
        pc_gcp = self.env.ref('partner_identification_gln.'
                              'partner_identification_gcp_number_category')
        self.partner_id_gcp_category = pc_gcp

        vals = {'name': '545053',
                'category_id': self.partner_id_gcp_category.id
                }
        self.company.partner_id.write({'id_numbers': [(0, 0, vals)]})

        self.env.user.company_id = self.company

    def test_serial_01(self):
        pack_obj = self.env['stock.quant.package']

        pack_1 = pack_obj.create({'name': 'PACK001',
                                  'ul_id': self.ul_1.id})

        self.assertEqual(False, not pack_1.serial_id)

        self.assertEqual('545053000000000015', pack_1.serial_id.name)
