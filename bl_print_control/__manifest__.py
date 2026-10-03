# Copyright 2026 SBINFO
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Contrôle de l'impression du BL",
    "summary": "Pas d'impression du BL à la signature, ni à la validation "
    "pour les clients qui n'en veulent pas",
    "version": "19.0.1.0.0",
    "category": "Inventory/Inventory",
    "author": "SBINFO",
    "website": "https://github.com/sbinfo67/odoo-report-print-send",
    "license": "AGPL-3",
    "depends": ["stock", "base_report_to_printer"],
    "data": ["views/res_partner_views.xml"],
    "installable": True,
    "application": False,
}
