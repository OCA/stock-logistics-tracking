# -*- coding: utf-8 -*-
# Copyright 2016 ACSONE S.A.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class StockPackagingSerial(models.Model):

    _name = 'stock.packaging.serial'
    _description = 'Stock Packaging Serial'

    name = fields.Char(string='Serial')


class ProductPackaging(models.Model):
    _inherit = 'product.packaging'

    gs1_barcode_id = fields.Many2one('gs1_barcode', string='Barcode GS1')

    package_sequence_id = fields.Many2one('ir.sequence',
                                          string='Barcode Sequence')

    automated_serial = fields.Boolean(string='Automated Serial',
                                      compute='_compute_automated_serial')

    @api.multi
    def _compute_automated_serial(self):

        for pack in self:
            if pack.gs1_barcode_id and pack.package_sequence_id:
                pack.automated_serial = True
            else:
                pack.automated_serial = False

    @api.multi
    def next_serial(self):
        # Methods get_serial_xxxx have to be defined in other modules
        # The parameters depends on implementation
        # e.g. : A header and a sequence
        self.ensure_one()
        sequence = ''

        if not self.gs1_barcode_id:
            raise Exception('No Barcode Application associated to package')

        method = 'next_serial_' + str(self.gs1_barcode_id.ai)
        func = False
        try:
            func = getattr(self, method)
        except AttributeError:
            pass

        if callable(func):
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

        if res and res.packaging_id:

            if res.packaging_id.automated_serial:
                sp_obj = self.env['stock.packaging.serial']
                serial = res.packaging_id.next_serial()
                ser = sp_obj.create({'name': serial})
                res.serial_id = ser

        return res

    @api.multi
    def write(self, vals):
        for package in self:
            # If We change the logistical unit for the package,
            # serial has to change
            if 'packaging_id' in vals:
                packaging_id = self.env['product.packaging'].browse(
                    vals.get('packaging_id', False))
                if packaging_id and packaging_id.automated_serial:
                    serial = packaging_id.next_serial()
                    sp_obj = self.env['stock.packaging.serial']
                    ser = sp_obj.create({'name': serial})
                    vals.update({'serial_id': ser.id})
        res = super(StockQuantPackage, self).write(vals)
        return res
