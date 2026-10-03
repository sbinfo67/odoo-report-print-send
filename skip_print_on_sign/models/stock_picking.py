# Copyright 2026 SBINFO
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models


class StockPicking(models.Model):
    _inherit = "stock.picking"

    def _attach_sign(self):
        # La signature rend le BL en PDF pour l'archiver dans le chatter.
        # base_report_to_printer enverrait ce rendu à l'imprimante quand le
        # rapport est en « Send to Printer » : la clé de contexte l'en empêche
        # sans toucher à l'impression faite à la validation.
        return super(
            StockPicking, self.with_context(must_skip_send_to_printer=True)
        )._attach_sign()
