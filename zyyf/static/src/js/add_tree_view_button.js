console.log($('button.o_list_button_add').text());
odoo.define('zyyf.add_tree_view_button', function (require) {
    "use strict";

    var core = require('web.core');
    var data = require('web.data');
    var ListView = require('web.ListView');
    var Widget = require('web.Widget');
    var ControlPanelMixin = require('web.ControlPanelMixin');

    var QWeb = core.qweb;
    var _t = core._t;
    var _lt = core._lt;
    var StateMachine = window.StateMachine;
    var Model = require('web.DataModel');


    console.log('loading......');

    // function generate_purchase_order() {
    //     var self = this;
    //     console.log(this.dataset.model);
    //     // console.log(this.getParent().action.context);
    //     this.do_action({
    //         type: 'ir.actions.client',
    //         tag: 'import_ljp',
    //         params: {
    //             model: this.dataset.model,
    //             // this.dataset.get_context() could be a compound?
    //             // not sure. action's context should be evaluated
    //             // so safer bet. Odd that timezone & al in it
    //             // though
    //             context: this.getParent().action.context,
    //         },{
    //             on_reverse_breadcrumb: function () {
    //                 return self.reload();
    //             },*/
    //     });
    // };

    ListView.include({
        render_buttons: function () {
            var self = this;
            this._super.apply(this, arguments); // Sets this.$buttons
            var button = $("<button type='button' class='btn btn-sm btn-default'>导入excel</button>")
                .click(this.proxy('generate_purchase_order'));
            this.$buttons.append(button);
        },
        generate_purchase_order: function () {
            // console.log(this.dataset.model);
            // console.log(this.getParent().action.context);
            this.do_action({
                type: 'ir.actions.client',
                tag: 'import_ljp',
                params: {
                    model: this.dataset.model,
                    // this.dataset.get_context() could be a compound?
                    // not sure. action's context should be evaluated
                    // so safer bet. Odd that timezone & al in it
                    // though
                    context: this.getParent().action.context,
                },
            }, {
                on_reverse_breadcrumb: function () {
                    return self.reload();
                },
            });
        },

    });

    var DataImport_ljp = Widget.extend(ControlPanelMixin, {
        template: 'ImportView_ljp',
        opts: [
            {name: 'encoding', label: _lt("Encoding:"), value: 'utf-8'},
            {name: 'separator', label: _lt("Separator:"), value: ','},
            {name: 'quoting', label: _lt("Text Delimiter:"), value: '"'}
        ],
        parse_opts: [
            {name: 'date_format', label: _lt("Date Format:"), value: ''},
            {name: 'datetime_format', label: _lt("Datetime Format:"), value: ''},
            {name: 'float_thousand_separator', label: _lt("Thousands Separator:"), value: ','},
            {name: 'float_decimal_separator', label: _lt("Decimal Separator:"), value: '.'}
        ],
        init: function (parent, action) {
            this._super.apply(this, arguments);
            var self = this;
            console.log(action.params.model);
            this.action_manager = parent;
            this.res_model = action.params.model;
            this.parent_context = action.params.context || {};
            // import object id
            this.id = null;
            this.Import = new Model('base_import.import');
            this.session = session;
            action.display_name = _t('Import a File'); // Displayed in the breadcrumbs
            this.do_not_change_match = false;
        },
        start: function () {
            var self = this;
            // this.setup_encoding_picker();
            // this.setup_separator_picker();
            // this.setup_float_format_picker();

            return $.when(
                this._super(),
                self.create_model().done(function (id) {
                    self.id = id;
                    self.$('input[name=import_id]').val(id);

                    // self.render_buttons();
                    var status = {
                        breadcrumbs: self.action_manager.get_breadcrumbs(),
                        cp_content: {$buttons: self.$buttons},
                    };
                    console.log(status);
                    self.update_control_panel(status);
                })
            );
        },
        create_model: function() {
            return this.Import.call('create', [{
                    'res_model': this.res_model
                }]);
        },
        // render_buttons: function() {
        //     var self = this;
        //     this.$buttons = $(QWeb.render("ImportView.buttons", this));
        //     this.$buttons.filter('.o_import_validate').on('click', this.validate.bind(this));
        //     this.$buttons.filter('.o_import_import').on('click', this.import.bind(this));
        //     this.$buttons.filter('.o_import_cancel').on('click', function(e) {
        //         e.preventDefault();
        //         self.exit();
        //     });
        // },
    });
    core.action_registry.add('import_ljp', DataImport_ljp);
});
