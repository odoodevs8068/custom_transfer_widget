from odoo import models, fields, api, _


class SaleOrderInherit(models.Model):
    _inherit = 'stock.move'

    @api.model
    def product_transfer_details(self, picking_ids, product_id):
        pick_ids = f"""in {tuple(picking_ids)}""" if len(picking_ids) > 1 else f"""= {picking_ids[0]}"""
        self.env.cr.execute(f"""
           SELECT
                sm.reference AS ref,
                sm.picking_id AS id,
                uom.name->>'en_US' AS name_2,
                SUM(sm.product_uom_qty) AS qty_1,
                COALESCE(ROUND(reserved_data.reserved_qty, 3), 0) AS qty_2,
                'stock.picking' AS model_name
           FROM stock_move sm
           LEFT JOIN (
                SELECT
                    sml.move_id,
                    SUM(sml.quantity) AS reserved_qty
                FROM stock_move_line sml
                GROUP BY sml.move_id
            ) reserved_data ON reserved_data.move_id = sm.id
           LEFT JOIN uom_uom uom ON uom.id = sm.product_uom
           WHERE
                sm.picking_id IS NOT NULL
                AND sm.picking_id {pick_ids} AND sm.product_id = {product_id}
                AND sm.state NOT IN ('done', 'cancel')
            GROUP BY
                picking_id, sm.reference,uom.name, reserved_data.reserved_qty;
            ;
        """)
        transfer_details = self.env.cr.dictfetchall()
        keys = ['Reference', 'Demand', 'Reserved', 'Uom']
        return transfer_details, keys

