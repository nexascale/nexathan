from nexathan.auth.tests.auth_backends import (BackendTest,
    RowlevelBackendTest, AnonymousUserBackendTest, NoAnonymousUserBackendTest,
    NoBackendsTest, InActiveUserBackendTest, NoInActiveUserBackendTest)
from nexathan.auth.tests.basic import BasicTestCase
from nexathan.auth.tests.decorators import LoginRequiredTestCase
from nexathan.auth.tests.forms import (UserCreationFormTest,
    AuthenticationFormTest, SetPasswordFormTest, PasswordChangeFormTest,
    UserChangeFormTest, PasswordResetFormTest)
from nexathan.auth.tests.remote_user import (RemoteUserTest,
    RemoteUserNoCreateTest, RemoteUserCustomTest)
from nexathan.auth.tests.management import GetDefaultUsernameTestCase
from nexathan.auth.tests.models import ProfileTestCase
from nexathan.auth.tests.signals import SignalTestCase
from nexathan.auth.tests.tokens import TokenGeneratorTest
from nexathan.auth.tests.views import (PasswordResetTest,
    ChangePasswordTest, LoginTest, LogoutTest, LoginURLSettings)
from nexathan.auth.tests.permissions import TestAuthPermissions

# The password for the fixture data users is 'password'
