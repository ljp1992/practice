odoo.define('add_button_in_tree_view.import_ljp', function (require) {
    "use strict";

    var core = require('web.core');
    var Model = require('web.Model');

    var download_excel_js = function (element, action) {
        var model = action.context.model;
        var field = action.context.field;
        var id = action.context.id;
        var filename = action.context.filename;
        var url = '/web/binary/download_document/?model='+model+'&field='+field+'&id='+id+'&filename='+filename;
        console.log(url);
        window.location.href = url;
    };

    core.action_registry.add('download_excel_ljp', download_excel_js);
});