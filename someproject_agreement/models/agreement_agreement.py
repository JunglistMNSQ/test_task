from odoo import api, fields, models, _


class AgreementAgreement(models.Model):
    _name = "agreement.agreement"
    _inherit = ["mail.thread"]
    _description = "Agreements"

    number = fields.Char(
        readonly=True,
        copy=False,
    )
    partner_id = fields.Many2one(
        "res.partner",
        string="Customer",
        required=True,
        tracking=True,
    )
    kind_id = fields.Many2one(
        "agreement.type",
        string="Agreement Type",
        required=True,
        tracking=True,
    )
    state = fields.Selection(
        [
            ("draft", "Draft"),
            ("approval", "Waiting Approval"),
            ("active", "Active"),
            ("done", "Done"),
        ],
        required=True,
        default="draft",
        tracking=True,
    )
    start_date = fields.Date(
        required=True,
        tracking=True,
    )
    end_date = fields.Date(
        required=True,
        tracking=True,
    )
    author_id = fields.Many2one(
        "res.users",
        string="Author",
        related="create_uid",
    )

    @api.model
    def create(self, vals):
        """
        Set number on creation.
        """
        next_code = self.env["ir.sequence"].next_by_code("agrmnt")
        if not next_code:
            sequence_vals = {
                "name": _("Agreement"),
                "code": "agrmnt",
                "implementation": "standard",
                "prefix": "AN/%(y)s/",
                "suffix": "",
                "padding": 6,
            }
            self.env["ir.sequence"].create(sequence_vals)
            next_code = self.env["ir.sequence"].next_by_code("agrmnt")
        vals["number"] = next_code
        return super().create(vals)

    def action_send_to_approve(self):
        """
        Change status to Waiting Approval.
        """
        self.write({"state": "approval"})
        return True

    def action_approve(self):
        """
        Change state to active.
        """
        self.write({"state": "active"})
        return True

    def send_for_revision(self):
        """
        Change state to draft and notify a document owner about revision.
        """
        self.write({"state": "draft"})
        for agreement in self:
            agreement.notify_about_revision()
        return True

    def notify_about_revision(self):
        """
        Notify about a revision necessary.
        """
        self.ensure_one()
        mail_template = self.env.ref(
            "someproject_agreement.mail_template_notify_agreement_revision", raise_if_not_found=False)
        if mail_template:
            mail_vals = mail_template.generate_email(self.id, ["subject", "body_html"])
            self.message_post(
                partner_ids=self.author_id.partner_id.ids,
                body=mail_vals["body_html"],
                subject=mail_vals["subject"],
                message_type="email",
            )

    def close_expired_agreements(self):
        """
        Set a done state on expired agreements.
        """
        self.search([
            ("state", "=", "active"),
            ("end_date", "<", fields.Date.today()),
        ]).write({"state": "done"})
