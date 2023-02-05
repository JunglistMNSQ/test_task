from datetime import timedelta
from unittest.mock import patch

from odoo import fields
from odoo.tests import common, Form, tagged


@tagged("-at_install", "post_install", "someproject")
class TestAgreementAgreement(common.TransactionCase):
    def setUp(self):
        """
        Setup test data.
        """
        super().setUp()
        self.agreement_obj = self.env["agreement.agreement"]
        self.agreement_type = self.env["agreement.type"].create({
            "name": "Test Agreement Type",
        })
        self.agreement = self.agreement_obj.create({
            "partner_id": self.ref("base.res_partner_1"),
            "kind_id": self.agreement_type.id,
            "start_date": fields.Date.today(),
            "end_date": fields.Date.today() + timedelta(days=5),
        })

    def test_readonly_attribute_in_not_draft_statuses(self):
        """
        Test protected fields.
        """
        protected_fields = [
            "partner_id",
            "kind_id",
            "start_date",
            "end_date",
        ]
        statuses_with_readonly = [
            "approval", "active", "done",
        ]
        for state in statuses_with_readonly:
            self.agreement.write({"state": state})
            agreement_form = Form(self.agreement)

            for field in protected_fields:
                with self.assertRaises(AssertionError) as e:
                    setattr(agreement_form, field, None)
                self.assertTrue(str(e.exception).startswith("can't write on readonly field"))

    @patch("odoo.addons.someproject_agreement.models.agreement_agreement."
           "AgreementAgreement.notify_about_revision")
    def test_notify_about_revision(self, notify_about_revision):
        """
        Test notify about revision.
        """
        agreement = self.agreement
        agreement.write({"state": "approval"})
        agreement.send_for_revision()
        notify_about_revision.assert_called_once()
        self.assertEqual(agreement.state, "draft")

    def test_cron_for_expired_agreements(self):
        """
        Test set a state done after cron.
        """
        agreement = self.agreement
        agreement.write({
            "state": "active",
            "end_date": fields.Date.today() + timedelta(days=-5),
        })
        self.agreement_obj.close_expired_agreements()
        self.assertEqual(agreement.state, "done")
