{
    'name': 'Transfer Widgets',
    'version': '1.2',
    'category': 'Extra Tools',
    'author': "JD DEVS",
    'depends': ['base', 'base_setup',  'sale', 'sale_stock', 'web', 'stock', 'mrp', 'purchase'],
    'data': [
        'views/transfer.xml',
    ],
    'assets': {
        'web.assets_backend': [
            "transfer_widget/static/src/widgets/transfer_widget.js",
            "transfer_widget/static/src/widgets/transfer_widget.xml",
            "transfer_widget/static/src/widgets/popover.css",
        ]
    },
    "images": [
        "static/description/banner.png"
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
    'license': 'AGPL-3',
}

