# Copyright 2026 SBINFO
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Pas d'impression automatique du BL par client",
    "summary": "Option sur la fiche client pour ne pas imprimer le BL à la validation",
    "version": "19.0.1.0.0",
    "category": "Inventory/Inventory",
    "author": "SBINFO",
    "website": "https://github.com/sbinfo67/odoo-report-print-send",
    "license": "AGPL-3",
    "depends": ["stock"],
    "data": ["views/res_partner_views.xml"],
    "installable": True,
    "application": False,
}
