# -*- coding: utf-8 -*-
# Copyright 2016 ACSONE S.A.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import models, _


class ProductUl(models.Model):
    _inherit = 'product.ul'

    def next_serial_00(self):

        seq = self.package_sequence_id._next()

        length_max = self.gs1_barcode_id.length_max
        the_length = 0
        if length_max > 1:
            # We compute the length without digit
            the_length = length_max - 1

        header = self.env.user.company_id.partner_id.id_numbers
        if header:
            length = the_length - (len(header[0].name) + len(seq))
            if length < 0:

                seq = seq[-length:]
            else:
                seq = ('0' * length) + seq

            gs1_header = header[0].name + seq

            i = 0
            number = 0
            for num in reversed(gs1_header):
                if (i % 2) == 0:
                    number += int(int(num) * 3)
                else:
                    number += int(num)
                i += 1

            rest = (number % 10)
            digit = 10 - rest

            return gs1_header + str(digit)
