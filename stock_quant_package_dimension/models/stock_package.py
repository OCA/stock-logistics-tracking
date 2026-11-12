# Copyright 2019 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)
from odoo import api, fields, models


class StockPackage(models.Model):
    _inherit = "stock.package"

    pack_weight = fields.Float()
    pack_length = fields.Float(help="length")
    width = fields.Float("Pack Width", help="width")
    height = fields.Float("Pack Height", help="height")
    volume = fields.Float(
        "Pack Volume",
        digits=(8, 4),
        compute="_compute_volume",
        readonly=True,
        store=False,
        help="volume",
    )
    length_uom_id = fields.Many2one(
        # Same as stock.package.type
        "uom.uom",
        "Dimensions Units of Measure",
        help="UoM for pack length, height, width (based on lenght UoM)",
        default=lambda self: self.env[
            "product.template"
        ]._get_length_uom_id_from_ir_config_parameter(),
    )
    length_uom_name = fields.Char(
        # Same as stock.package.type
        string="Length unit of measure label",
        related="length_uom_id.name",
        readonly=True,
    )
    weight_uom_id = fields.Many2one(
        # Same as stock.package.type
        "uom.uom",
        string="Weight Units of Measure",
        help="Weight Unit of Measure",
        compute=False,
        default=lambda self: self.env[
            "product.template"
        ]._get_weight_uom_id_from_ir_config_parameter(),
    )
    weight_uom_name = fields.Char(
        # Same as stock.package.type
        string="Weight unit of measure label",
        compute="_compute_weight_uom_name",
    )
    volume_uom_id = fields.Many2one(
        # Same as stock.package.type
        "uom.uom",
        string="Volume Units of Measure",
        help="Packaging volume unit of measure",
        default=lambda self: self.env[
            "product.template"
        ]._get_volume_uom_id_from_ir_config_parameter(),
    )
    volume_uom_name = fields.Char(
        # Same as stock.package.type
        string="Volume Unit of Measure label",
        related="volume_uom_id.name",
        readonly=True,
    )

    @api.depends("weight_uom_id", "weight_uom_id.name")
    def _compute_weight_uom_name(self):
        # Don't use a related here as the original default value
        # causes warnings (Redundant default on related fields are not wanted)
        for package in self:
            package.weight_uom_name = package.weight_uom_id.name

    @api.depends(
        "pack_length",
        "width",
        "height",
        "length_uom_id",
        "volume_uom_id",
    )
    def _compute_volume(self):
        PackageType = self.env["stock.package.type"]
        for pack in self:
            pack.volume = PackageType._calculate_volume(
                pack.pack_length,
                pack.height,
                pack.width,
                pack.length_uom_id,
                pack.volume_uom_id,
            )

    def write(self, vals):
        res = super().write(vals)
        if vals.get("package_type_id"):
            self._update_dimensions_from_packaging(override=False)
        return res

    @api.model_create_multi
    def create(self, vals_list):
        packages = super().create(vals_list)
        for package, vals in zip(packages, vals_list, strict=True):
            package._update_dimensions_from_packaging(
                override=False,
                provided_fields=set(vals),
            )
        return packages

    def _update_dimensions_fields(self):
        # source: destination
        return {
            "packaging_length": "pack_length",
            "width": "width",
            "height": "height",
            "base_weight": "pack_weight",
        }

    def _update_dimensions_from_packaging(self, override=False, provided_fields=None):
        provided_fields = provided_fields or set()
        for package in self:
            if not package.package_type_id:
                continue
            package_type = package.package_type_id
            values = {}
            for source, dest in self._update_dimensions_fields().items():
                if dest in provided_fields:
                    continue
                if not override and package[dest]:
                    continue
                value = package_type[source]
                if source in ("packaging_length", "width", "height"):
                    # stock.package.type stores dimensions in the global
                    # length unit. It has no per-type length_uom_id field.
                    source_uom = package.env[
                        "product.template"
                    ]._get_length_uom_id_from_ir_config_parameter()
                    dest_uom = package.length_uom_id
                else:
                    # base_weight uses the global weight unit for the same
                    # reason: stock.package.type has no weight_uom_id field.
                    source_uom = package.env[
                        "product.template"
                    ]._get_weight_uom_id_from_ir_config_parameter()
                    dest_uom = package.weight_uom_id
                if value and source_uom and dest_uom:
                    value = source_uom._compute_quantity(
                        value,
                        dest_uom,
                        round=False,
                    )
                values[dest] = value
            if values:
                if package.id:
                    package.write(values)
                else:
                    package.update(values)

    @api.onchange("package_type_id")
    def onchange_package_type_id(self):
        self._update_dimensions_from_packaging(override=True)
