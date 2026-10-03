# Copyright 2026 SBINFO
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import Command
from odoo.tests import TransactionCase, tagged

DELIVERY_SLIP = "stock.report_deliveryslip"
RETURN_SLIP = "stock.report_return_document"


@tagged("post_install", "-at_install")
class TestPartnerNoAutoprint(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.warehouse = cls.env["stock.warehouse"].search(
            [("company_id", "=", cls.env.company.id)], limit=1
        )
        cls.warehouse.out_type_id.auto_print_delivery_slip = True
        cls.product = cls.env["product.product"].create({"name": "Pot de miel"})
        Partner = cls.env["res.partner"]
        cls.regular = Partner.create({"name": "Client normal", "is_company": True})
        cls.blocked = Partner.create(
            {
                "name": "Client sans BL",
                "is_company": True,
                "no_autoprint_delivery_slip": True,
            }
        )
        # Les livraisons partent en général vers une adresse de la société.
        cls.blocked_address = Partner.create(
            {"name": "Dépôt", "type": "delivery", "parent_id": cls.blocked.id}
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

    @staticmethod
    def _reports(actions):
        return {a["report_name"]: a["context"]["active_ids"] for a in actions}

    def test_regular_customer_prints(self):
        """Témoin : la validation imprime le BL d'un client normal."""
        picking = self._picking(self.regular)
        res = picking.button_validate()
        self.assertEqual(res["tag"], "do_multi_print")
        self.assertEqual(
            self._reports(res["params"]["reports"]), {DELIVERY_SLIP: [picking.id]}
        )

    def test_blocked_customer_does_not_print(self):
        """Livraison vers une adresse du client coché : pas de BL imprimé."""
        picking = self._picking(self.blocked_address)
        self.assertIs(picking.button_validate(), True)
        self.assertEqual(picking.state, "done")

    def test_mixed_validation_keeps_other_slips(self):
        """Validation groupée : seul le BL du client coché est retiré."""
        regular = self._picking(self.regular)
        blocked = self._picking(self.blocked)
        actions = (regular | blocked)._get_autoprint_report_actions()
        self.assertEqual(self._reports(actions), {DELIVERY_SLIP: [regular.id]})

    def test_other_autoprints_unchanged(self):
        """Le bon de retour reste imprimé pour le client coché."""
        self.warehouse.out_type_id.auto_print_return_slip = True
        picking = self._picking(self.blocked)
        actions = picking._get_autoprint_report_actions()
        self.assertEqual(self._reports(actions), {RETURN_SLIP: [picking.id]})

    def test_option_follows_company(self):
        """L'option se règle sur la société et suit sur ses adresses."""
        self.assertTrue(self.blocked_address.no_autoprint_delivery_slip)
        self.blocked.no_autoprint_delivery_slip = False
        self.assertFalse(self.blocked_address.no_autoprint_delivery_slip)
