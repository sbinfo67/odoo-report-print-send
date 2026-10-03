=====================================
Pas d'impression à la signature du BL
=====================================

Quand le client signe un bon de livraison (bouton **Signer** du transfert),
Odoo rend le BL signé en PDF et le joint au chatter. Si le rapport « Bon de
livraison » est réglé sur **Send to Printer** dans ``base_report_to_printer``,
ce rendu part aussi à l'imprimante. Ce module supprime cette impression-là.

Ce qui change, ce qui ne change pas :

* le PDF signé est toujours généré et joint au chatter ;
* l'impression du BL à la validation, ou depuis le menu Imprimer, reste
  inchangée.

Fonctionnement
==============

À l'enregistrement de la signature, ``stock.picking.write()`` appelle
``_attach_sign()``, qui rend le rapport ``stock.action_report_delivery`` par
``_render_qweb_pdf``. ``base_report_to_printer`` surcharge cette méthode et
envoie à l'imprimante tout rendu dont le comportement est « Send to Printer ».

Le module surcharge ``_attach_sign()`` et pose la clé de contexte
``must_skip_send_to_printer``, que ``_can_print_report`` de
``base_report_to_printer`` consulte avant tout envoi. La clé ne vit que le
temps de la signature.

Le champ « Domaine du filtre » du rapport ne peut pas servir à cela : il ne
filtre que l'entrée du menu Imprimer et n'est pas lu au rendu.

Installation
============

Le module se trouve dans le même dépôt que ``base_report_to_printer``. Mettre
à jour le dépôt sur le serveur, redémarrer Odoo, mettre à jour la liste des
applications, puis installer **Pas d'impression à la signature du BL**
(``skip_print_on_sign``).

Test manuel
===========

#. Valider un BL de test : il s'imprime, comme avant.
#. Le signer sur le smartphone : rien ne sort à l'imprimante, et le message
   « Order signed by … » apparaît dans le chatter avec le PDF signé.

Tests automatisés
=================

``tests/test_stock_picking_sign.py`` règle le BL sur Send to Printer et
intercepte l'envoi à l'imprimante :

* témoin : un rendu du BL hors signature imprime ;
* la signature n'imprime pas et joint bien le PDF signé ;
* la clé de contexte ne survit pas à la signature.

Sans le module, le deuxième test échoue (une impression). ::

    odoo -d <base> -i skip_print_on_sign --test-enable \
        --test-tags /skip_print_on_sign --stop-after-init

Auteur
======

SBINFO
