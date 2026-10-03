# Copyright 2026 SBINFO
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from unittest import mock

from odoo import Command
from odoo.tests import TransactionCase, tagged

PRINT_DOCUMENT = (
    "odoo.addons.base_report_to_printer.models.printing_printer."
    "PrintingPrinter.print_document"
)


@tagged("post_install", "-at_install")
class TestConfirmationEmail(TransactionCase):
    """Configuration de production : la société envoie l'e-mail de
    confirmation à la validation, et le BL est en « Send to Printer ».
    L'e-mail joint le BL, dont le rendu part alors à l'imprimante."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Avec base_report_to_printer_cups, une imprimante injoignable
        # (pas de serveur CUPS en test) bloque l'envoi : on l'ignore,
        # comme les tests d'OCA.
        cls.env = cls.env(context=dict(cls.env.context, skip_printer_exception=True))
        cls.env.company.stock_move_email_validation = True
        cls.env.ref("stock.action_report_delivery").write(
            {
                "property_printing_action_id": cls.env.ref(
                    "base_report_to_printer.printing_action_1"
                ).id,
                "printing_printer_id": cls.env["printing.printer"]
                .create({"name": "Imprimante BL", "system_name": "bl"})
                .id,
            }
        )
        cls.warehouse = cls.env["stock.warehouse"].search(
            [("company_id", "=", cls.env.company.id)], limit=1
        )
        cls.product = cls.env["product.product"].create({"name": "Pot de miel"})
        Partner = cls.env["res.partner"]
        cls.regular = Partner.create(
            {"name": "Client normal", "email": "normal@example.com"}
        )
        cls.blocked = Partner.create(
            {
                "name": "Client sans BL",
                "email": "sansbl@example.com",
                "no_autoprint_delivery_slip": True,
            }
        )

    def _picking(self, partner):
        customers = self.env.ref("stock.stock_location_customers")
        picking = self.env["stock.picking"].create(
            {
                "picking_type_id": self.warehouse.out_type_id.id,
                "partner_id": partner.id,
                "location_id": self.warehouse.lot_stock_id.id,
                "location_dest_id": customers.id,
                "move_ids": [
                    Command.create(
                        {
                            "product_id": self.product.id,
                            "product_uom_qty": 1.0,
                            "location_id": self.warehouse.lot_stock_id.id,
                            "location_dest_id": customers.id,
                        }
                    )
                ],
            }
        )
        picking.action_confirm()
        picking.move_ids.write({"quantity": 1.0, "picked": True})
        return picking

    def _emailed_slips(self, picking):
        return picking.message_ids.attachment_ids.filtered(
            lambda a: picking.name in a.name
        )

    def test_regular_customer_prints(self):
        """Témoin : l'e-mail de confirmation d'un client normal imprime le BL."""
        picking = self._picking(self.regular)
        with mock.patch(PRINT_DOCUMENT) as print_document:
            picking.button_validate()
        print_document.assert_called_once()
        self.assertTrue(self._emailed_slips(picking))

    def test_blocked_customer_does_not_print(self):
        """Client coché : l'e-mail part avec le BL, sans impression."""
        picking = self._picking(self.blocked)
        with mock.patch(PRINT_DOCUMENT) as print_document:
            picking.button_validate()
        print_document.assert_not_called()
        self.assertEqual(picking.state, "done")
        self.assertTrue(self._emailed_slips(picking))

    def test_mixed_validation(self):
        """Validation groupée : seul le BL du client normal s'imprime."""
        regular = self._picking(self.regular)
        blocked = self._picking(self.blocked)
        with mock.patch(PRINT_DOCUMENT) as print_document:
            (regular | blocked).button_validate()
        print_document.assert_called_once()
        self.assertTrue(self._emailed_slips(regular))
        self.assertTrue(self._emailed_slips(blocked))
