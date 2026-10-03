==============================
Contrôle de l'impression du BL
==============================

Supprime deux impressions du bon de livraison jugées inutiles, sans toucher
aux autres :

#. **À la signature** : le BL signé par le client n'est plus envoyé à
   l'imprimante. Il reste archivé dans le chatter.
#. **À la validation, pour certains clients** : une case sur la fiche client
   empêche l'impression automatique du BL quand on valide ses livraisons.

Le BL reste toujours imprimable à la main depuis le menu **Imprimer**.

Pas d'impression à la signature
===============================

Quand le client signe un BL (bouton **Signer** du transfert), Odoo rend le BL
signé en PDF et le joint au chatter. Si le rapport « Bon de livraison » est
réglé sur **Send to Printer** dans ``base_report_to_printer``, ce rendu part
aussi à l'imprimante. Le module supprime cette impression pour tous les
clients, sans réglage.

À l'enregistrement de la signature, ``stock.picking.write()`` appelle
``_attach_sign()``, qui rend le rapport ``stock.action_report_delivery`` par
``_render_qweb_pdf``. ``base_report_to_printer`` surcharge cette méthode et
envoie à l'imprimante tout rendu dont le comportement est « Send to Printer ».
Le module surcharge ``_attach_sign()`` et pose la clé de contexte
``must_skip_send_to_printer``, que ``_can_print_report`` consulte avant tout
envoi. La clé ne vit que le temps de la signature.

Le champ « Domaine du filtre » du rapport ne peut pas servir à cela : il ne
filtre que l'entrée du menu Imprimer et n'est pas lu au rendu.

Pas d'impression à la validation pour certains clients
======================================================

Case **Ne pas imprimer le BL à la validation** sur la fiche client, onglet
*Ventes & Achats*, bloc *Livraison*. Elle se règle sur la société. Odoo la
recopie sur ses contacts et adresses de livraison, où elle apparaît en
lecture seule.

Pour un client coché :

* la validation d'une livraison n'imprime plus le BL ;
* les autres impressions automatiques à la validation (bon de retour,
  étiquettes, colis) sont conservées ;
* dans une validation groupée, seuls les BL des autres clients s'impriment.

L'impression automatique vient du type d'opération des livraisons :
*Inventaire > Configuration > Types d'opérations*, onglet *Matériel*, case
*Bon de livraison* du bloc « Imprimer sur validation »
(``auto_print_delivery_slip``). Le module ne fait que retirer certains clients
de cette impression.

À la validation, ``button_validate`` demande à
``_get_autoprint_report_actions`` la liste des rapports à imprimer. Le
standard sélectionne les transferts sur le seul type d'opération, sans point
d'extension. Le module reprend le résultat et reconstruit l'action du BL sans
les transferts dont la société cliente (``commercial_partner_id``) est
cochée. S'il n'en reste aucun, l'action du BL est retirée.

Installation
============

Le module se trouve dans le même dépôt que ``base_report_to_printer``, dont il
dépend. Mettre à jour le dépôt sur le serveur, redémarrer Odoo, mettre à jour
la liste des applications, puis installer **Contrôle de l'impression du BL**
(``bl_print_control``).

Test manuel
===========

#. Valider le BL d'un client normal : il s'imprime, comme avant.
#. Le signer sur le smartphone : rien ne sort à l'imprimante, et le message
   « Order signed by … » apparaît dans le chatter avec le PDF signé.
#. Cocher la case sur un client, valider une de ses livraisons : rien ne sort
   à l'imprimante.

Tests automatisés
=================

``tests/test_stock_picking_sign.py`` règle le BL sur Send to Printer et
intercepte l'envoi à l'imprimante :

* témoin : un rendu du BL hors signature imprime ;
* la signature n'imprime pas et joint bien le PDF signé ;
* la clé de contexte ne survit pas à la signature.

``tests/test_partner_no_autoprint.py`` active l'impression du BL à la
validation sur les livraisons, puis vérifie :

* témoin : un client normal déclenche l'impression du BL ;
* une livraison vers une adresse d'un client coché n'imprime rien ;
* une validation groupée ne retire que le BL du client coché ;
* le bon de retour reste imprimé pour le client coché ;
* l'option suit la société sur ses adresses.

Sans la surcharge de ``stock.picking``, les quatre tests de blocage échouent
et les témoins passent. ::

    odoo -d <base> -i bl_print_control --test-enable \
        --test-tags /bl_print_control --stop-after-init

Auteur
======

SBINFO
