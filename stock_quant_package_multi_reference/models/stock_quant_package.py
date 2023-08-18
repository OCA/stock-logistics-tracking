# © 2023 Cetmix OÜ
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import _, api, fields, models


class StockQuantPackage(models.Model):
    _inherit = "stock.quant.package"

    reference_ids = fields.One2many(
        comodel_name="stock.quant.package.reference",
        inverse_name="stock_quant_package_id",
        string="References",
    )
    name = fields.Char(
        string="Package Reference",
        default=lambda self: self.env["ir.sequence"].next_by_code("stock.quant.package")
        or _("Unknown Pack"),
        compute="_compute_reference",
        store=True,
        inverse="_inverse_reference",
        compute_sudo=True,
        index="trigram",
        copy=False,
    )

    @api.depends("reference_ids.name", "reference_ids.sequence")
    def _compute_reference(self):
        for package in self:
            package.name = package.reference_ids[:1].name

    def _inverse_reference(self):
        """Store the package's reference value in the reference model."""
        packages_to_unlink = self.env["stock.quant.package.reference"]
        create_reference_vals_list = []
        for package in self:
            if package.reference_ids:
                package.reference_ids[0].name = package.name
            elif not package.name:
                packages_to_unlink |= package.reference_ids
            else:
                create_reference_vals_list.append(package._prepare_reference_vals())
        if packages_to_unlink:
            packages_to_unlink.unlink()
        if create_reference_vals_list:
            self.env["stock.quant.package.reference"].create(create_reference_vals_list)

    def _prepare_reference_vals(self):
        self.ensure_one()
        return {
            "stock_quant_package_id": self.id,
            "name": self.name,
        }

    @api.model
    def _search(self, domain, *args, **kwargs):
        for sub_domain in list(filter(lambda x: x[0] == "name", domain)):
            domain = self._get_reference_domain(sub_domain, domain)
        return super(StockQuantPackage, self)._search(domain, *args, **kwargs)

    def _get_reference_domain(self, sub_domain, domain):
        reference_operator = sub_domain[1]
        reference_value = sub_domain[2]
        references = self.env["stock.quant.package.reference"].search(
            [("name", reference_operator, reference_value)]
        )
        domain = [
            ("reference_ids", "in", references.ids)
            if x[0] == "name" and x[2] == reference_value
            else x
            for x in domain
        ]
        return domain
