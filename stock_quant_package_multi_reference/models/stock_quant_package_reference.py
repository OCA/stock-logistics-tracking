# © 2023 Cetmix OÜ
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class StockQuantPackageReference(models.Model):
    _name = "stock.quant.package.reference"
    _description = "Individual item in a package's reference list"
    _order = "sequence, id"

    name = fields.Char(
        string="Reference",
        required=True,
    )
    sequence = fields.Integer(
        default=0,
    )
    stock_quant_package_id = fields.Many2one(
        string="Package",
        comodel_name="stock.quant.package",
        ondelete="cascade",
    )

    @api.constrains("name")
    def _check_duplicates(self):
        for record in self:
            reference = self.search(
                [("id", "!=", record.id), ("name", "=", record.name)], limit=1
            )
            if reference:
                # by default reference 'shared' between all company (no ir.rule)
                # so we may not have the access right on the package
                # note: if you do not want to share the reference between company
                # you just need to add a custom ir.rule
                package = reference.sudo().stock_quant_package_id
                raise ValidationError(
                    _(
                        'The Reference "%(reference_name)s" already exists for '
                        'package "%(package_name)s" in the company %(company_name)s'
                    )
                    % dict(
                        reference_name=reference.name,
                        package_name=package.name,
                        company_name=package.company_id.name,
                    )
                )
