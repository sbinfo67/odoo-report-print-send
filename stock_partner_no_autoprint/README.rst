=============================================
Pas d'impression automatique du BL par client
=============================================

Ajoute sur la fiche client une case **Ne pas imprimer le BL à la
validation** (onglet *Ventes & Achats*, bloc *Livraison*). Pour un client
coché, la validation d'une livraison n'imprime plus le bon de livraison.

Ce qui change, ce qui ne change pas :

* le BL reste imprimable depuis le menu **Imprimer** du transfert ;
* les autres impressions automatiques à la validation (bon de retour,
  étiquettes, colis) sont conservées ;
* les autres clients ne sont pas concernés, y compris dans une validation
  groupée mêlant les deux cas.

L'option se règle sur la société. Odoo la recopie sur ses contacts et adresses
de livraison, où elle apparaît en lecture seule.

Prérequis
=========

L'impression automatique vient du type d'opération des livraisons :
*Inventaire > Configuration > Types d'opérations*, onglet *Matériel*, case
*Bon de livraison* du bloc « Imprimer sur validation »
(``auto_print_delivery_slip``). Le module ne fait que retirer certains clients
de cette impression.

Avec ``base_report_to_printer`` réglé sur *Send to Printer*, c'est cette même
impression qui part à l'imprimante : elle est donc supprimée aussi. Le module
ne dépend pas de ``base_report_to_printer`` et fonctionne sans lui.

Fonctionnement
==============

À la validation, ``button_validate`` demande à
``_get_autoprint_report_actions`` la liste des rapports à imprimer. Le
standard sélectionne les transferts sur le seul type d'opération, sans point
d'extension. Le module reprend le résultat et reconstruit l'action du BL sans
les transferts dont la société cliente (``commercial_partner_id``) est
cochée. S'il n'en reste aucun, l'action du BL est retirée.

Tests automatisés
=================

``tests/test_partner_no_autoprint.py`` active l'impression du BL à la
validation sur les livraisons, puis vérifie :

* témoin : un client normal déclenche l'impression du BL ;
* une livraison vers une adresse d'un client coché n'imprime rien ;
* une validation groupée ne retire que le BL du client coché ;
* le bon de retour reste imprimé pour le client coché ;
* l'option suit la société sur ses adresses.

Sans la surcharge de ``stock.picking``, les trois tests de blocage échouent. ::

    odoo -d <base> -i stock_partner_no_autoprint --test-enable \
        --test-tags /stock_partner_no_autoprint --stop-after-init

Auteur
======

SBINFO
