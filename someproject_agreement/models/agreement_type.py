from odoo import fields, models


class AgreementType(models.Model):
    _name = "agreement.type"
    _inherit = ["mail.thread"]
    _description = "Type of Agreements"

    active = fields.Boolean(
        default=True,
        tracking=True,
    )
    name = fields.Char(
        required=True,
        tracking=True,
    )

    _sql_constraints = [
        ("unique_agreement_type_by_name", "UNIQUE(name)", "The name should be unique!"),
    ]
