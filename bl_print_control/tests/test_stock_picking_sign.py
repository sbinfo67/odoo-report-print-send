# Copyright 2026 SBINFO
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from unittest import mock

from odoo import Command
from odoo.tests import TransactionCase, tagged

PRINT_DOCUMENT = (
    "odoo.addons.base_report_to_printer.models.printing_printer."
    "PrintingPrinter.print_document"
)

# PNG 1x1, le champ signature est un fields.Image qui refuse un contenu factice.
SIGNATURE = (
    b"iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA"
    b"60e6kgAAAABJRU5ErkJggg=="
)


@tagged("post_install", "-at_install")
class TestStockPickingSign(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Avec base_report_to_printer_cups, une imprimante injoignable
        # (pas de serveur CUPS en test) bloque l'envoi : on l'ignore,
        # comme les tests d'OCA.
        cls.env = cls.env(context=dict(cls.env.context, skip_printer_exception=True))
        # L'e-mail de confirmation imprime aussi le BL : testé à part dans
        # test_confirmation_email, coupé ici quel que soit le réglage.
        cls.env.company.stock_move_email_validation = False
        # Même réglage qu'en production : le BL part à l'imprimante.
        cls.report = cls.env.ref("stock.action_report_delivery")
        cls.report.write(
            {
                "property_printing_action_id": cls.env.ref(
                    "base_report_to_printer.printing_action_1"
                ).id,
                "printing_printer_id": cls.env["printing.printer"]
                .create({"name": "Imprimante BL", "system_name": "bl"})
                .id,
            }
        )
        warehouse = cls.env["stock.warehouse"].search(
            [("company_id", "=", cls.env.company.id)], limit=1
        )
        product = cls.env["product.product"].create({"name": "Pot de miel"})
        cls.picking = cls.env["stock.picking"].create(
            {
                "picking_type_id": warehouse.out_type_id.id,
                "partner_id": cls.env["res.partner"].create({"name": "Client"}).id,
                "location_id": warehouse.lot_stock_id.id,
                "location_dest_id": cls.env.ref("stock.stock_location_customers").id,
                "move_ids": [
                    Command.create(
                        {
                            "product_id": product.id,
                            "product_uom_qty": 1.0,
                            "location_id": warehouse.lot_stock_id.id,
                            "location_dest_id": cls.env.ref(
                                "stock.stock_location_customers"
                            ).id,
                        }
                    )
                ],
            }
        )
        cls.picking.action_confirm()
        cls.picking.move_ids.write({"quantity": 1.0, "picked": True})
        cls.picking.button_validate()

    def test_delivery_slip_render_prints(self):
        """Témoin : hors signature, le rendu du BL part à l'imprimante."""
        self.assertEqual(self.picking.state, "done")
        with mock.patch(PRINT_DOCUMENT) as print_document:
            self.env["ir.actions.report"]._render_qweb_pdf(
                "stock.action_report_delivery", self.picking.id
            )
        print_document.assert_called_once()

    def test_sign_does_not_print(self):
        """La signature archive le BL signé sans l'imprimer."""
        with mock.patch(PRINT_DOCUMENT) as print_document:
            self.picking.write({"signature": SIGNATURE})
        print_document.assert_not_called()
        self.assertIn(
            f"{self.picking.name}_signed_delivery_slip.pdf",
            self.picking.message_ids.attachment_ids.mapped("name"),
        )

    def test_sign_context_does_not_leak(self):
        """La clé de contexte ne survit pas à la signature."""
        self.picking.write({"signature": SIGNATURE})
        with mock.patch(PRINT_DOCUMENT) as print_document:
            self.env["ir.actions.report"]._render_qweb_pdf(
                "stock.action_report_delivery", self.picking.id
            )
        print_document.assert_called_once()
