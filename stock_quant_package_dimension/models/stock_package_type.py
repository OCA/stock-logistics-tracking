# Copyright 2019 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)
from odoo import models


class StockPackageType(models.Model):
    _inherit = "stock.package.type"

    def _calculate_volume(
        self, packaging_length, height, width, length_uom_id, volume_uom_id
    ):
        volume_m3 = 0
        if packaging_length and height and width and length_uom_id:
            length_m = self.convert_to_meters(packaging_length, length_uom_id)
            height_m = self.convert_to_meters(height, length_uom_id)
            width_m = self.convert_to_meters(width, length_uom_id)
            volume_m3 = length_m * height_m * width_m
        volume_in_volume_uom = self.convert_to_volume_uom(volume_m3, volume_uom_id)
        return volume_in_volume_uom

    def convert_to_meters(self, measure, length_uom_id):
        uom_meters = self.env.ref("uom.product_uom_meter")
        return length_uom_id._compute_quantity(
            qty=measure,
            to_unit=uom_meters,
            round=False,
        )

    def convert_to_volume_uom(self, measure, volume_uom_id):
        uom_m3 = self.env.ref("uom.product_uom_cubic_meter")
        return uom_m3._compute_quantity(
            qty=measure,
            to_unit=volume_uom_id,
            round=False,
        )
