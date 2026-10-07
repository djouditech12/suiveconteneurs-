{
    'name': 'Container Tracking',
    'version': '19.0.1.0.0',
    'category': 'Inventory/Logistics',
    'icon': '/container_tracking/static/description/icon.png',
    'summary': 'Track containers imported from China (in transit / arrived)',
    'description': """
Container Tracking
==================
* Container number, departure date from China, expected arrival date
* Content: bags, shoes, total quantity of pieces
* Statuses: In Transit / Arrived
* Supplier, freight forwarder and port (optional)
* List, kanban and calendar views, filters, grouping and search
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
