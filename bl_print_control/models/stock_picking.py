# Copyright 2026 SBINFO
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models

from odoo.addons.web.controllers.utils import clean_action


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

    def _filter_no_autoprint(self):
        return self.filtered(
            "partner_id.commercial_partner_id.no_autoprint_delivery_slip"
        )

    def _send_confirmation_email(self):
        # L'e-mail de confirmation joint le BL en PDF : avec « Send to
        # Printer », ce rendu part à l'imprimante. C'est l'impression « à la
        # validation » des sociétés qui envoient cet e-mail. L'e-mail reste
        # envoyé, seul l'envoi à l'imprimante est retenu.
        blocked = self._filter_no_autoprint()
        if blocked:
            super(
                StockPicking, blocked.with_context(must_skip_send_to_printer=True)
            )._send_confirmation_email()
        return super(StockPicking, self - blocked)._send_confirmation_email()

    def _get_autoprint_report_actions(self):
        # Le standard filtre les transferts sur le seul type d'opération, sans
        # point d'extension : on reconstruit l'action du BL sans les clients
        # qui l'ont refusé. Les autres impressions automatiques (bon de
        # retour, étiquettes, colis) restent telles quelles.
        report_actions = super()._get_autoprint_report_actions()
        blocked = self._filter_no_autoprint()
        if not blocked:
            return report_actions
        delivery_report = self.env.ref("stock.action_report_delivery")
        to_print = (
            self.filtered(lambda p: p.picking_type_id.auto_print_delivery_slip)
            - blocked
        )
        result = []
        for action in report_actions:
            if action.get("report_name") != delivery_report.report_name:
                result.append(action)
            elif to_print:
                action = delivery_report.report_action(to_print.ids, config=False)
                clean_action(action, self.env)
                result.append(action)
        return result
