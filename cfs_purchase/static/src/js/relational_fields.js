odoo.define('cfs_purchase.RelationalFields', function (require) {
    "use strict";

    var RelationalFields = require('web.relational_fields')
    RelationalFields.FieldMany2One.include({
        /**
         * @override
         * EOI136 - include name in the dynamic context
         */
        _createContext: function (name) {
            var tmp = {};
            var field = this.nodeOptions.create_name_field;
            if (field === undefined) {
                field = "name";
            }
            if (field !== false && name && this.nodeOptions.quick_create !== false) {
                tmp["default_" + field] = name;
                if (name.includes('@')) {
                    tmp["default_email"] = name;
                }

            }
            return tmp;
        },
    })
});