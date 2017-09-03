odoo.define('cfprint.qdoo_xml_print', function (require) {
    "use strict";

    var core = require('web.core');
    var Model = require('web.Model');

    var Qdoo_Xml_Print = function (element, action) {
        var model = action.context.model;
        var field = action.context.field;
        var id = action.context.id;
        var filename = action.context.filename;
        var url = '/web/binary/download_document/?model='+model+'&field='+field+'&id='+id+'&filename='+filename;
        window.location.href = url;
    };

    core.action_registry.add('qdoo_xml_print', Qdoo_Xml_Print);
});