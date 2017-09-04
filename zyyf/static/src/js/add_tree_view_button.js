console.log($('button.o_list_button_add').text());
odoo.define('zyyf.add_tree_view_button', function (require) {
    "use strict";

    var ListView = require('web.ListView');

    ListView.include({
        render_buttons: function () {
            this._super.apply(this, arguments);
            this.$buttons.children().each(function () {
                if ($(this).hasClass('o_button_import')){
                    console.log('have');
                    $(this).hide();
                }
            });
            if (this.dataset.model == 'customer'){
                var button = $("<button type='button' class='btn btn-sm btn-default'>导入</button>")
                    .click(this.proxy('import_excel_ljp'));
                this.$buttons.append(button);
            }
        },
        import_excel_ljp: function () {
            this.do_action({
                type: 'ir.actions.act_window',
                res_model: 'import.wizard',
                views: [[false, 'form']],
                view_mode: "form",
                view_type: 'form',
                target: 'new',
            });
        },
    });

});
