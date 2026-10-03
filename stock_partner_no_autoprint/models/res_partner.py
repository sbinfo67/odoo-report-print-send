# Copyright 2026 SBINFO
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    no_autoprint_delivery_slip = fields.Boolean(
        string="Ne pas imprimer le BL à la validation",
        help="Les livraisons de ce client ne déclenchent pas l'impression "
        "automatique du bon de livraison à la validation. Le BL reste "
        "imprimable depuis le menu Imprimer.",
    )

    @api.model
    def _commercial_fields(self):
        # Réglé sur la société, recopié sur ses contacts et adresses de
        # livraison.
        return super()._commercial_fields() + ["no_autoprint_delivery_slip"]
