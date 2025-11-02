/** @odoo-module **/

import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";
import { usePopover } from "@web/core/popover/popover_hook";
import { Component } from "@odoo/owl";
import { standardWidgetProps } from "@web/views/widgets/standard_widget_props";
import { WarningDialog } from "@web/core/errors/error_dialogs";
import { _t } from "@web/core/l10n/translation";

/**
 * ------------------------------------------------------------------------
 * TransferPopover — Inner component showing transfer details inside a popover
 * ------------------------------------------------------------------------
 */
export class TransferPopover extends Component {
    static template = "transfer_widget.StockTransferWidget";
    static props = {
        record: Object,
        calcData: Object,
        close: Function,
        transfer_ids: { type: Array, optional: true },
    };

    setup() {
        this.orm = useService("orm");
        this.actionService = useService("action");
    }

    /**
     * Open full list of transfers
     */
    async AllTransfer() {
        this.actionService.doAction({
            type: 'ir.actions.act_window',
            name: 'Transfers',
            res_model: 'stock.picking',
            view_mode: 'list,form',
            views: [[false, 'list'], [false, 'form']],
            target: 'current',
            domain: [['id', 'in', this.props.transfer_ids]],
            context: {
                create: false,
            },
        });
    }

    /**
     * Open a single transfer record
     */
    async onOpenTransfer(ev) {
        const { id, model } = ev.currentTarget.dataset;
        if (!id || !model) {
            return;
        }

        await this.actionService.doAction({
            type: "ir.actions.act_window",
            res_model: model,
            res_id: parseInt(id),
            view_mode: "form",
            views: [[false, "form"]],
            target: "new",
            context: { create: false, edit: false },
        });
    }
}

/**
 * ------------------------------------------------------------------------
 * StockTransferWidget — Main widget that triggers the popover
 * ------------------------------------------------------------------------
 */
export class StockTransferWidget extends Component {
    static template = "transfer_widget.TransferWidget";
    static components = { Popover: TransferPopover };
    static props = { ...standardWidgetProps };

    setup() {
        this.orm = useService("orm");
        this.action = useService("action");
        this.dialog = useService("dialog");
        this.popover = usePopover(TransferPopover, { position: "top",  popoverClass: "o_transfer_popover transfer-popover "});
        this.field_name = null;
        this.field_model = null;
        this.source_name = null;
        this.transfer_ids = [];
    }
    async onTransferPopover(ev) {
        const target = ev.currentTarget;
        const model = this.props.record._config.resModel;
        const resId = this.props.record._config.resId || this.props.record.model.config.resId;

        const _parentRecordId = this.props.record?._parentRecord?._config?.resId || this.props.record?._config?.resId
        const _parentRecordModel = this.props.record?._parentRecord?._config?.resModel || this.props.record?._config?.resModel
        const SearchPickings = await this.orm.searchRead(_parentRecordModel,[['id', '=', _parentRecordId]],['picking_ids']);

        if (SearchPickings[0]?.picking_ids.length == 0) {
            return this._showWarning(_t("There are no transfers for this record."));
        }
        const picking_ids = SearchPickings[0].picking_ids
        console.log("this.props.record.data.product_id", this.props.record.data.product_id)
        const data = await this.orm.call("stock.move", "product_transfer_details", [picking_ids, this.props.record.data.product_id['id']]);

        const transferLines = data?.[0] || [];
        const transferIds = transferLines.map((line) => line.id || 0);
        if (!transferLines.length) {
            return this._showWarning(_t("There are no transfers for this record."));
        }
        this.popover.open(target, {
            record: this.props.record,
            calcData: data,
            transfer_ids: transferIds,
        });
    }

    _showWarning(message) {
        this.dialog.add(WarningDialog, {
            title: _t("Warning"),
            message,
        });
    }
}

/**
 * ------------------------------------------------------------------------
 * Registry
 * ------------------------------------------------------------------------
 */
registry.category("view_widgets").add("transfer_widget", {
    component: StockTransferWidget,
});
