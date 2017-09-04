odoo.define('add_button_in_tree_view.add_tree_view_button', function (require) {
    "use strict";

    var core = require('web.core');
    var data = require('web.data');
    var ListView = require('web.ListView');
    var Widget = require('web.Widget');
    var ControlPanelMixin = require('web.ControlPanelMixin');
    var session = require('web.session');
    var ViewManager = require('web.ViewManager');


    var QWeb = core.qweb;
    var _t = core._t;
    var _lt = core._lt;
    var StateMachine = window.StateMachine;
    var Model = require('web.DataModel');


    console.log('loading...1...');


    ListView.include({
        render_buttons: function () {
            var self = this;
            this._super.apply(this, arguments); // Sets this.$buttons
            var button2 = $("<button type='button' class='btn btn-sm btn-default'>导入excel</button>")
                .click(this.proxy('generate_purchase_order'));
            this.$buttons.append(button2);
        },
        generate_purchase_order: function () {
            console.log('execute import');
            this.do_action({
                type: 'ir.actions.act_window',
                res_model: 'import.wizard',
                // res_id: move_id,
                views: [[false, 'form']],
                view_mode: "form",
                view_type: 'form',
                target: 'new',
            });
        },

    });

});
