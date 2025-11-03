from odoo import models, fields, api, _

class StockInherit(models.Model):
    _inherit = 'stock.move'

    @api.model
    def product_transfer_details(self, picking_ids, product_id):
        pick_ids = f"""in {tuple(picking_ids)}""" if len(picking_ids) > 1 else  f"""= {picking_ids[0]}"""
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

    @api.model
    def product_details(self, line_id, product_id):
        query = f"""
                    SELECT
                        spl.name AS ref,
                        sq.id AS id,
                        SUM(quantity) AS qty_1,  
                        SUM(quantity) - SUM(reserved_quantity) AS qty_2,
    					SUM(reserved_quantity) AS name_2,
    					'stock.quant' AS model_name
                    FROM 
                        stock_quant sq
                    LEFT JOIN stock_lot spl ON sq.lot_id = spl.id 	
                    LEFT JOIN stock_location sl ON sl.id = sq.location_id 
                    LEFT JOIN stock_location sl_sl ON sl_sl.id = sl.location_id
                    WHERE
                        sq.product_id = {product_id}
                        AND sq.company_id IS NOT NULL 
                        AND sq.quantity > 0 
                        AND sq.inventory_date IS NOT NULL 
                        AND sl.usage = 'internal'
                    GROUP BY 
                        spl.name, sq.id;
                """
        self._cr.execute(query)
        Onhandqty_by_lot = self._cr.dictfetchall()
        keys = ['Lot', 'Onhand Qty', 'Available Qty', 'Reserved Qty']
        return Onhandqty_by_lot, keys


