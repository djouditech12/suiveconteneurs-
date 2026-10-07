{
    'name': 'Suivi des Conteneurs',
    'version': '19.0.1.0.0',
    'category': 'Inventory/Logistics',
    'summary': "Suivi des conteneurs importés de Chine (en route / arrivé)",
    'description': """
Suivi des conteneurs
====================
* Numéro de conteneur, date de départ de Chine, date d'arrivée prévue
* Contenu : sacs, chaussures, quantité totale de pièces
* Statuts : En route / Arrivé
* Vues liste, kanban, calendrier, filtres, regroupements et recherche
""",
    'author': 'Djoudi Tech',
    'license': 'LGPL-3',
    'depends': ['base', 'mail'],
    'data': [
        'security/container_security.xml',
        'security/ir.model.access.csv',
        'views/container_tracking_views.xml',
        'views/menus.xml',
    ],
    'application': True,
    'installable': True,
}
