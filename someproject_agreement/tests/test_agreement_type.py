from odoo.tests import common, tagged


@tagged("-at_install", "post_install", "someproject")
class TestAgreementType(common.TransactionCase):
    def setUp(self):
        """
        Setup test data.
        """
        super().setUp()
        self.agreement_type_obj = self.env["agreement.type"]
        self.agreement_type_obj.create({"name": "Test Agreement Type"})

    def test_unique_name(self):
        """
        Test unique SQL constraint.
        """
        with self.assertRaises(Exception) as e:
            self.agreement_type_obj.create({"name": "Test Agreement Type"})

        self.assertTrue(str(e.exception).endswith("Key (name)=(Test Agreement Type) already exists.\n"))
