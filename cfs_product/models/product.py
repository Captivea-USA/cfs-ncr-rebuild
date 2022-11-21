from odoo import fields, models, api, _
from odoo.exceptions import UserError


class ProductTemplate(models.Model):

    _inherit = "product.template"

    # EOI-387: Add cfs_autoexec module
    # TODO: These domains are commented so they return as an empty list because we do not 
    # have permissions set up yet. They will need to be updated when we have permissions.
    @api.model
    def _design_owner_domain(self):
        return [
            # ("id", "in", self.env.ref("cfs_product.cfs_group_owner_design"))
        ]

    @api.model
    def _mfg_owner_domain(self):
        return [
            # ("id", "in", self.env.ref("cfs_product.cfs_group_owner_mfg").users.ids)
        ]

    @api.model
    def _procurement_owner_domain(self):
        return [
            # (
            #     "id",
            #     "in",
            #     self.env.ref("cfs_product.cfs_group_owner_procurement").users.ids,
            # )
        ]

    @api.model
    def _planner_owner_domain(self):
        return [
            # ("id", "in", self.env.ref("cfs_product.cfs_group_owner_planner").users.ids)
       ]

    is_hazardous = fields.Boolean(string="Hazardous")
    eccn = fields.Char("ECCN")
    version = fields.Integer(
        "Current Revision", default=1, help="The current version of the product."
    )
    version_char = fields.Char(
        string="Version", default="A", help="The current version of the product."
    )
    part_status = fields.Selection(
        [
            ("active", "Released"),
            ("development", "In Development"),
            ("revision", "Under Revision"),
            ("obsolete", "Obsolete"),
        ],
        string="Status",
        copy=False,
        index=True,
        tracking=3,
        default="development",
        compute="_compute_part_status",
        store=True,
        readonly=False,
    )
    # ITERP 52
    yield_pc = fields.Float("Yield (%)", tracking=1, default=100.00, digits=(3, 2))

    #ITERP 46
    weight_uom = fields.Selection([('0','kg'),('1','g')], string='Weight UoM', default='0', tracking=1)
    volume_uom = fields.Selection([('0','ft³'),('1','in³')], string='Volume UoM', default='0', tracking=1)
    uom_less_weight = fields.Float('Weight',tracking=1)
    uom_less_volume = fields.Float('Volume',tracking=1)

    procurement_type = fields.Selection(related="categ_id.procurement_type")
    critical_part = fields.Boolean("Critical Part", default=False, tracking=1)
    source_controlled = fields.Boolean("Source Controlled", default=False, tracking=1)
    log_lead_time = fields.Boolean("Long Lead Time", default=False, tracking=1)
    can_override_gl = fields.Boolean(string="Can override", default=False)
    allowed_loc_ids = fields.Many2many(
        comodel_name="stock.location",
        string="Allowed Locations",
    )
    design_owner = fields.Many2one(
        "res.users", "Design Owner", tracking=1, domain=_design_owner_domain
    )
    mfg_owner = fields.Many2one(
        "res.users", "Mfg. Owner", tracking=1, domain=_mfg_owner_domain
    )
    procurement_owner = fields.Many2one(
        "res.users", "Procurement Owner", tracking=1, domain=_procurement_owner_domain
    )
    # todo commodity code is needed bc it sets proc owner
    commodity_code = fields.Char("Commodity Code")
    commodity_code_id = fields.Many2one(
        comodel_name="commodity.code", string="Commodity"
    )
    responsible_id = fields.Many2one(
        "res.users",
        string="Planner",
        company_dependent=False,
        check_company=False,
        domain=_planner_owner_domain,
        default=False,
        help="This user will be assigned any activities related to logistic operations for this product.",
    )

    quality_codes = fields.Many2many(
        comodel_name="product.quality.code", string="Quality Codes"
    )

    stock_warn = fields.Selection(
        [
            ("no-message", "No Message"),
            ("warning", "Warning"),
            ("block", "Block Message"),
        ],
        string="Stock Warning",
        default="no-message",
    )
    stock_warn_msg = fields.Text(string="Warning Message")

    @api.model
    def create(self, vals):
        """Create Method
        Raise error if hazardous and no warning is selected
        Write same cfs code for all variants

        Args:
            vals (vals): the values being used

        Returns:
            create call: parent call to create
        """
        if vals.get("is_hazardous") and vals.get("stock_warn") == "no-message":
            raise UserError(
                "Hazardous products require a 'Warning when Moving this Product'.  Enter this on the Inventory tab."
            )

        if vals.get("default_code"):
            for variant in self.product_variant_ids:
                variant.write({"default_code": vals["default_code"]})
        return super().create(vals)

    def write(self, values):
        """Write Method
        Raise error if hazardous and no warning is selected
        Write same cfs code for all variants
        disallow setting to development when product is active
        disallow setting part status if obsolete
        test version char

        Args:
            vals (vals): the values being used

        Returns:
            write call: parent call to write
        """
        # test hazardous for setting stock_warn
        if values.get("is_hazardous"):
            for record in self:
                if record.is_hazardous and record.stock_warn == "no-message":
                    raise UserError(
                        "Hazardous products require a 'Warning when Moving this Product'.  Enter this on the Inventory tab."
                    )

        if values.get("default_code"):
            for variant in self.product_variant_ids:
                variant.write({"default_code": values["default_code"]})

        # create part status and version
        if "part_status" in values:
            if self.part_status == "active" and values["part_status"] == "development":
                raise UserError(_("Cannot set product back to in development"))
            elif self.part_status == "obsolete" and values["part_status"]:
                raise UserError(_("Product is obsolete"))
        ver = ""
        if "version_char" in values:
            ver = values["version_char"]
            no_version_attr = True
            for line in self.attribute_line_ids:
                if line.attribute_id.name == "Revision":
                    no_version_attr = False
                    val = self.env["product.attribute.value"].search([("name", "=", ver), ("attribute_id", "=", line.attribute_id.id)])
                    if len(val.ids) >= 1:
                        line.write({
                            "value_ids": [(4, val.ids[0], 0)]
                        })
                    elif len(val.ids) == 0:
                        line.write({
                            "value_ids": [(0, 0, {"name": ver, "attribute_id": line.attribute_id.id})]
                        })
            if no_version_attr:
                attr = self.env["product.attribute"].search([("name", "=", "Revision")])
                try:
                    val = self.env["product.attribute.value"].search([("name", "=", ver), ("attribute_id", "=", attr.id)])
                    self.env["product.template.attribute.line"].create({
                        "product_tmpl_id": self.id,
                        "attribute_id": attr.id,
                        "value_ids": [(4, val.ids[0], 0)]
                    })
                except:
                    self.env["product.template.attribute.line"].create({
                        "product_tmpl_id": self.id,
                        "attribute_id": attr.id,
                        "value_ids": [(0, 0, {"name": ver, "attribute_id": attr.id})]
                    })

        return super().write(values)


    @api.depends("eco_ids")
    def _compute_part_status(self):
        """if eco stage changed to effective, put part status in revision
        """
        for temp in self:
            for eco in temp.eco_ids:
                if eco.stage_id.name != "Effective":
                    temp.part_status = "revision"

    @api.depends("product_variant_ids", "product_variant_ids.default_code")
    def _compute_default_code(self):
        """compute default code if variants are changed
        """
        unique_variants = self.filtered(
            lambda template: len(template.product_variant_ids) == 1
        )
        for template in unique_variants:
            template.default_code = template.default_code
        for template in self - unique_variants:
            template.default_code = template.default_code

    @api.onchange("commodity_code_id", "categ_id")
    def _onchange_commodity_code(self):
        """TODO not sure what this does"""
        for rec in self:
            if rec.commodity_code_id:
                rec.commodity_code = rec.commodity_code_id.code
            if rec.commodity_code_id and rec.procurement_type == "direct":
                rec.procurement_owner = rec.commodity_code_id.owner_id.id
                rec.quality_codes = [(6, 0, rec.commodity_code_id.code_ids.ids)]
                newven = self.env.ref("cfs_product.newven").id
                sellers = rec.seller_ids.filtered(
                    lambda seller: seller.name.id == newven
                )
                for seller in sellers:
                    seller.delay = rec.commodity_code_id.lead_time
                if len(sellers) == 0 and len(rec.seller_ids) == 0:
                    vals = {
                        "name": newven,
                        "delay": rec.commodity_code_id.lead_time,
                        "product_tmpl_id": rec.id,
                        "product_uom": rec.uom_po_id,
                    }
                    self.env["product.supplierinfo"].create(vals)


class ProductCategory(models.Model):

    _inherit = "product.category"

    procurement_type = fields.Selection(
        [("direct", "Direct"), ("indirect", "Indirect")],
        string="Procurement Type",
        required="1",
        default="direct",
    )
    description_ids = fields.Many2many("account.tolerance.description", string="Tolerance Description")

    can_override_gl_categ = fields.Boolean(string="Can override", default=False)

class ProductProduct(models.Model):
    _inherit = 'product.product'

    @api.model_create_multi
    def create(self, vals_list):
        """Ensure default code is unique
        """
        for vals in vals_list:
            if vals.get('default_code') and self.env["product.product"].search_count([("default_code", "=", vals['default_code']), ("product_tmpl_id", "!=", vals.get('product_tmpl_id'))]) > 0:
                raise UserError("Internal Reference is not unique")
            tmpl = self.env["product.template"].browse([vals.get('product_tmpl_id')])
            if vals.get('default_code') != tmpl.default_code:
                vals['default_code'] = tmpl.default_code
        return super(ProductProduct, self.with_context(create_product_product=True)).create(vals_list)

    def write(self, values):
        """Ensure default code is unique
        """
        result = super(ProductProduct, self).write(values)
        if values.get('default_code') and self.env["product.product"].search_count([("default_code", "=", values['default_code']), ("product_tmpl_id", "!=", self.product_tmpl_id.id)]) > 0:
            raise UserError("Internal Reference is not unique")
        return result

    # EOI-426: Part and description should be separated on the PO/PR
    def name_get(self):
        ####### removed the part where it won't display hte pricelist product name of the vendor
        def _name_get(d):
            code = self._context.get('display_default_code', True) and d.get('default_code', False) or False
            name = code if code else d.get('name', '')
            return (d['id'], name)
        partner_id = self._context.get('partner_id')
        if partner_id:
            partner_ids = [partner_id, self.env['res.partner'].browse(partner_id).commercial_partner_id.id]
        else:
            partner_ids = []
        company_id = self.env.context.get('company_id')

        # all user don't have access to seller and partner
        # check access and use superuser
        self.check_access_rights("read")
        self.check_access_rule("read")

        result = []
        self.sudo().read(['name', 'default_code', 'product_tmpl_id'], load=False)

        product_template_ids = self.sudo().mapped('product_tmpl_id').ids

        for product in self.sudo():
            variant = product.product_template_attribute_value_ids._get_combination_name()

            name = variant and "%s (%s)" % (product.name, variant) or product.name
      
            mydict = {
                        'id': product.id,
                        'name': name,
                        'default_code': product.default_code,
                        }
            result.append(_name_get(mydict))
        return result