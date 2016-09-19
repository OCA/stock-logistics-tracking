# -*- coding: utf-8 -*-
# Copyright 2016 ACSONE S.A.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import api, fields, models, _


class StockPackagingSerial(models.Model):

    _name = 'stock.packaging.serial'
    _description = 'Stock Packaging Serial'

    name = fields.Char(string='Serial')


class ProductUl(models.Model):
    _inherit = 'product.ul'

    gs1_barcode_id = fields.Many2one('gs1_barcode', string='Barcode GS1')

    package_sequence_id = fields.Many2one('ir.sequence',
                                          string='Barcode Sequence')

    automated_serial = fields.Boolean(compute='_get_automated_serial')

    @api.multi
    def _get_automated_serial(self):

        for ul in self:
            if ul.gs1_barcode_id and ul.package_sequence_id:
                ul.automated_serial = True
            else:
                ul.automated_serial = False

    @api.multi
    def next_serial(self):
        self.ensure_one()
        sequence = ''

        '''
        Methods get_serial_xxxx have to be defined in other modules
        The parameters depends on implementation
        e.g. : A header and a sequence
        '''

        if not self.gs1_barcode_id:
            raise Exception('No Barcode Application associated to package')

        method = 'next_serial_' + str(self.gs1_barcode_id.ai)
        if callable(getattr(self, method)):
            serial_function = getattr(self, method)
            sequence = serial_function()
        else:
            if self.package_sequence_id:
                sequence = self.package_sequence_id._next()

        return sequence


class StockQuantPackage(models.Model):
    _inherit = 'stock.quant.package'

    serial_id = fields.Many2one('stock.packaging.serial',
                                string='Serial Number')

    @api.model
    def create(self, vals):
        res = super(StockQuantPackage, self).create(vals)

        if res and res.ul_id:

            if res.ul_id.automated_serial:
                sp_obj = self.env['stock.packaging.serial']
                serial = res.ul_id.next_serial()
                ser = sp_obj.create({'name': serial})
                res.serial_id = ser

        return res

    @api.multi
    def write(self, vals):
        for package in self:
            # If We change the logistical unit for the package,
            # serial has to change
            if 'ul_id' in vals:
                ul = self.env['product.ul'].browse(vals.get('ul_id', False))
                if ul and ul.automated_serial:
                    serial = package.ul_id.next_serial()
                    sp_obj = self.env['stock.package.serial']
                    ser = sp_obj.create({'name': serial})
                    vals.update({'serial_id': ser})
        res = super(StockQuantPackage, self).write(vals)
        return res
