from odoo.tests import common

"""Common Tests 

Inherit this class in any test classes to add functionality to send a helpful message to console for test pass/fail

If any errors are detected in the test, you simply append to the class variable `assertionErrors` like so:

try:
    self.assertTrue("something")
except AssertionError as aex:
    self.assertionErrors.append(aex)

Upon the teardown of eact test, if any entries are detected in `assertionErrors`, a message is sent in a print statement
in red text (on linux) that the test name has failed with the specified error. If no errors are detected, then a message is sent
in a print statement in blue text that the test has passed

TODO:
    a false pass can still occur if the written test runs into an error
"""

class ExportsCommon(common.SavepointCase):
    assertionFunction = "No test provided"
    def setAssertionFunction(cls, value):
        """
        Set string variable
        """
        cls.assertionFunction = value

    @classmethod
    def setUpClass(cls):
        """
        Setup products/account for making purchase orders
        """

        super().setUpClass()
        print(f'{bcolors.BOLD}Multi Level Approval{bcolors.ENDC}')
        cls.assertionErrors = []

    @classmethod
    def tearDown(cls):
        # print any errors and then reset the assertion list
        if not cls.assertionErrors:
            print(f"{bcolors.OKBLUE}✓ Pass: {cls.assertionFunction}{bcolors.ENDC}")
        else:
            for error in cls.assertionErrors:
                print(
                    f"{bcolors.FAIL}X Fail: {cls.assertionFunction}: {error}{bcolors.ENDC}"
                )
        cls.assertionErrors = []

def setAssertionFunction(value):
    ExportsCommon.assertionFunction = value


class bcolors:
    HEADER = "\033[95m"
    OKBLUE = "\033[94m"
    OKCYAN = "\033[96m"
    OKGREEN = "\033[92m"
    WARNING = "\033[93m"
    FAIL = "\033[91m"
    ENDC = "\033[0m"
    BOLD = "\033[1m"
    UNDERLINE = "\033[4m"