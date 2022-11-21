

from .common import ExportsCommon,setAssertionFunction

class TestMultiApprovalLine(ExportsCommon):
    def test_create(self):
        """
        EOI695 - Test that we receive the proper exceptions
        """
        setAssertionFunction("test_create")
        error_approval_level = 52
        low_approval_level = 20
        high_approval_level = 70
        duplicate_approval_level = 40
        passing_name = 'BudgetOwnername'
        passing_approval_level = 50
        passing_user_id = 17
        passing_status = 'new'
        passing_minimum = 1
        try:
            # at least one user is set as approver
            with self.assertRaises(Exception) as context:
                self.env['multi.approval.line'].create({
                    'name': passing_name, 
                    'user_id': False, 
                    'level': 52, 
                    'min_approval': 0, 
                    'everyone_approves': False, 
                    'user_ids': [[6, False, []]], 
                    'status': False, 
                    'approval_id': 13934
                })
            self.assertTrue(f'You must add at least one user to the approval' in str(context.exception))
            # level is multiple of 10
            with self.assertRaises(Exception) as context:
                self.env['multi.approval.line'].create({
                    'name': passing_name, 
                    'user_id': passing_user_id, 
                    'level': error_approval_level, 
                    'min_approval': 0, 
                    'everyone_approves': False, 
                    'user_ids': [[6, False, [passing_user_id]]], 
                    'status': False, 
                    'approval_id': 13934
                })
            self.assertTrue(f'Approval level must be a multiple of level 10. Detected level: {error_approval_level}' in str(context.exception))
            # Level cannot be less than the highest level on the apprvoal
            with self.assertRaises(Exception) as context:
                self.env['multi.approval.line'].create({
                    'name': passing_name, 
                    'user_id': passing_user_id, 
                    'level': low_approval_level, 
                    'min_approval': 0, 
                    'everyone_approves': False, 
                    'user_ids': [[6, False, [passing_user_id]]], 
                    'status': False, 
                    'approval_id': 13934
                })
            self.assertTrue(f"Approval level must be higher than the highest level on the order 40 and less than the maximum level 60. Detected level: {low_approval_level}" in str(context.exception))
            # Level cannot be higher than the maximum level of 60 on the apprvoal
            with self.assertRaises(Exception) as context:
                self.env['multi.approval.line'].create({
                    'name': passing_name, 
                    'user_id': passing_user_id, 
                    'level': high_approval_level, 
                    'min_approval': 0, 
                    'everyone_approves': False, 
                    'user_ids': [[6, False, [passing_user_id]]], 
                    'status': False, 
                    'approval_id': 13934
                })
            self.assertTrue(f"Approval level must be higher than the highest level on the order 40 and less than the maximum level 60. Detected level: {high_approval_level}" in str(context.exception))
            # Level cannot be the same as another level on the appoval
            with self.assertRaises(Exception) as context:
                self.env['multi.approval.line'].create({
                    'name': passing_name, 
                    'user_id': passing_user_id, 
                    'level': duplicate_approval_level, 
                    'min_approval': 0, 
                    'everyone_approves': False, 
                    'user_ids': [[6, False, [passing_user_id]]], 
                    'status': False, 
                    'approval_id': 13934
                })
            self.assertTrue(f"The custom approval level {duplicate_approval_level} already exists on this approval. Please edit the existing level." in str(context.exception))

            # Creating without a status gives an error
            with self.assertRaises(Exception) as context:
                self.env['multi.approval.line'].create({
                    'name': passing_name, 
                    'user_id': passing_user_id, 
                    'level': passing_approval_level, 
                    'min_approval': 0, 
                    'everyone_approves': False, 
                    'user_ids': [[6, False, [passing_user_id]]], 
                    'status': False, 
                    'approval_id': 13934
                })
            self.assertTrue(f'Status must be set as new.' in str(context.exception))
            # Creating without the minimum approval gives an error
            with self.assertRaises(Exception) as context:
                self.env['multi.approval.line'].create({
                    'name': passing_name, 
                    'user_id': passing_user_id, 
                    'level': passing_approval_level, 
                    'min_approval': 0, 
                    'everyone_approves': False, 
                    'user_ids': [[6, False, [passing_user_id]]], 
                    'status': passing_status, 
                    'approval_id': 13934
                })
            self.assertTrue(f'Minimum to approve must be at least one' in str(context.exception))
            # Creating without the minimum approval gives an error
            rec = self.env['multi.approval.line'].create({
                'name': passing_name, 
                'user_id': passing_user_id, 
                'level': passing_approval_level, 
                'min_approval': passing_minimum, 
                'everyone_approves': False, 
                'user_ids': [[6, False, [passing_user_id]]], 
                'status': passing_status, 
                'approval_id': 13934
            })
            self.assertTrue(rec)
            # test that sending context will bypass the checks
            rec = self.env['multi.approval.line'].with_context({'item': 'new_bill'}).create({
                'name': passing_name, 
                'user_id': passing_user_id, 
                'level': passing_approval_level, 
                'min_approval': passing_minimum, 
                'everyone_approves': False, 
                'user_ids': [[6, False, [passing_user_id]]], 
                'status': passing_status, 
                'approval_id': 13934
            })
            self.assertTrue(rec)
        except Exception as err:
            self.assertionErrors.append(err)

    def test_unlink(self):
        """EOI695 - test that unlinking will properly delete the record, 
        also test that chatter properly appears
        """
        setAssertionFunction("test_unlink")
        username = "Bob Mumgaard"
        multi_approval_id = 13934
        multi_approval_line_id = 16736
        try:
            multi_approval_line = self.env['multi.approval.line'].browse(multi_approval_line_id)
            res = multi_approval_line.unlink()
            self.assertTrue(res)
            # test chatter
            chatter_area = self.env['mail.message'].search(
                [("res_id", "=", multi_approval_id), ("model", "=", "multi.approval")]
            )
            self.assertIn(f'<p>Level 40 deleted -{username}. </p>', [chat.body for chat in chatter_area])
        except Exception as err:
            self.assertionErrors.append(err)

    def test_write(self):
        """EOI695 - test that unlinking will properly delete the record, 
        this just test that no exception occurs
        """
        setAssertionFunction("test_write")
        user_id_40 = 4685
        username_40 = "Bill Jellesma"
        username_30 = "Tracy Jin"
        multi_approval_id = 13967
        multi_approval_line_id_40 = 16786
        multi_approval_line_id_30 = 16785
        try:
            # This level already has 4606 so it should show one user added
            res = self.env['multi.approval.line'].browse(multi_approval_line_id_40).write({
                'user_ids': [[6, False, [4606, user_id_40]]]
            })
            self.assertTrue(res)
            # test chatter add
            chatter_area = self.env['mail.message'].search(
                [("res_id", "=", multi_approval_id), ("model", "=", "multi.approval")]
            )
            self.assertIn(f'<p>Level 40 updated - Users Added: {username_40}. </p>', [chat.body for chat in chatter_area])
            # test chatter remove
            res = self.env['multi.approval.line'].browse(multi_approval_line_id_30).write({
                'user_ids': [[6, False, [4739, 4663, 4752, 4735, 173]]]
            })
            chatter_area = self.env['mail.message'].search(
                [("res_id", "=", multi_approval_id), ("model", "=", "multi.approval")]
            )
            self.assertIn(f'<p>Level 30 updated - Users Removed: {username_30}. </p>', [chat.body for chat in chatter_area])
        except Exception as err:
            self.assertionErrors.append(err)

    