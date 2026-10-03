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

Le BL peut s'imprimer à la validation par deux chemins. La case couvre les
deux.

**L'e-mail de confirmation de livraison** (*Inventaire > Configuration >
Paramètres*, « Confirmation par e-mail », réglage par société). À la
validation, Odoo envoie au client un e-mail avec le BL en pièce jointe. Avec
``base_report_to_printer`` en *Send to Printer*, rendre cette pièce jointe
envoie aussi le BL à l'imprimante. Pour un client coché, l'e-mail part
toujours avec son BL, mais rien n'est imprimé.

``_send_confirmation_email`` est surchargé : les transferts des clients cochés
y passent avec la clé de contexte ``must_skip_send_to_printer``, les autres
sans. Les surcharges de ``point_of_sale`` et ``stock_sms`` appellent la
méthode standard sur un sous-ensemble : la clé leur parvient.

**L'impression automatique du type d'opération** (*Inventaire > Configuration
> Types d'opérations*, onglet *Matériel*, case *Bon de livraison* du bloc
« Imprimer sur validation », ``auto_print_delivery_slip``). À la validation,
``button_validate`` demande à ``_get_autoprint_report_actions`` la liste des
rapports à imprimer. Le standard sélectionne les transferts sur le seul type
d'opération, sans point d'extension. Le module reprend le résultat et
reconstruit l'action du BL sans les transferts des clients cochés. S'il n'en
reste aucun, l'action du BL est retirée. Les autres impressions automatiques
(bon de retour, étiquettes, colis) sont conservées.

Dans les deux cas, lors d'une validation groupée, seuls les BL des autres
clients s'impriment. Le client coché est cherché sur la société
(``commercial_partner_id``) du partenaire du transfert.

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
   à l'imprimante, et le client reçoit quand même l'e-mail avec son BL.

Tests automatisés
=================

``tests/test_stock_picking_sign.py`` règle le BL sur Send to Printer et
intercepte l'envoi à l'imprimante :

* témoin : un rendu du BL hors signature imprime ;
* la signature n'imprime pas et joint bien le PDF signé ;
* la clé de contexte ne survit pas à la signature.

``tests/test_confirmation_email.py`` reprend la configuration de production :
e-mail de confirmation activé, BL en Send to Printer.

* témoin : l'e-mail d'un client normal imprime le BL ;
* client coché : l'e-mail part avec le BL, sans impression ;
* validation groupée : seul le BL du client normal s'imprime.

``tests/test_partner_no_autoprint.py`` active l'impression du BL à la
validation sur le type d'opération, puis vérifie :

* témoin : un client normal déclenche l'impression du BL ;
* une livraison vers une adresse d'un client coché n'imprime rien ;
* une validation groupée ne retire que le BL du client coché ;
* le bon de retour reste imprimé pour le client coché ;
* l'option suit la société sur ses adresses.

Les tests valent avec ou sans ``base_report_to_printer_cups`` : ils posent
``skip_printer_exception``, comme ceux d'OCA, faute de serveur CUPS en test.
Sans la surcharge de ``stock.picking``, les six tests de blocage échouent. ::

    odoo -d <base> -i bl_print_control --test-enable \
        --test-tags /bl_print_control --stop-after-init

Auteur
======

SBINFO
