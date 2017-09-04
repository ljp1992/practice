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

    // function download_template() {
    //     console.log('download template file');
    //     var url = '/web/binary/download_document/?model=excel.template&field=template_file&id=1&filename=cs.xlsx';
    //     window.location.href = url;
    // }

    console.log('loading...3...');


    ListView.include({
        render_buttons: function () {
            var self = this;
            this._super.apply(this, arguments); // Sets this.$buttons
            // var button1 = $("<button type='button' class='btn btn-sm btn-default'>下载模板</button>")
            //     .click(this.proxy('download_template'));
            // this.$buttons.append(button1);
            var button2 = $("<button type='button' class='btn btn-sm btn-default'>导入excel</button>")
                .click(this.proxy('generate_purchase_order'));
            this.$buttons.append(button2);
        },
        generate_purchase_order: function () {
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
        events: {
            'change .select_file_ljp': function (e) {
                var file = this.$('.oe_import_file')[0].files[0];
                console.log(file);
                var val = this.$('.oe_import_file')[0].value;
                console.log(val);
                this.$('.oe_import_file_show').val(file !== undefined && file.name || '');
                $.ajax({
                    type: 'POST',
                    url: '/base_import_ljp/set_file',
                    dataType: 'json',
                    // beforeSend: function(xhr){xhr.setRequestHeader('Content-Type', 'application/json');},
                    data: {
                        file: val,
                        file_name: file.name,
                    },
                    success: function(data) {
                        console.log('upload success');
                    },
                });
            },
        },
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
            action.display_name = _t('导入excel'); // Displayed in the breadcrumbs
            // this.do_not_change_match = false;
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
        // download_template: function () {
        //     console.log('download template file');
        //     var url = '/web/binary/download_document/?model=excel.template&field=template_file&id=1&filename=cs.xlsx';
        //     window.location.href = url;
        // }
    });
    core.action_registry.add('import_ljp', DataImport_ljp);

    StateMachine.create({
        target: DataImport_ljp.prototype,
        events: [],
    });

    return {
        DataImport: DataImport,
}


});
