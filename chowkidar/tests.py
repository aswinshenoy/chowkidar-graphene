import graphene
from django.contrib.auth import get_user_model
from django.test import TestCase

from chowkidar.graphql import AuthMutations

User = get_user_model()


class Mutation(AuthMutations):
    pass


class Query(graphene.ObjectType):
    test = graphene.Boolean()


schema = graphene.Schema(mutation=Mutation, query=Query)


class AuthenticateUserTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.validUsername = "aswinshenoy"
        cls.validPassword = "W3@kP@$$w0rb!"
        cls.validEmail = "aswinshenoy65@gmail.com"

        cls.user = User.objects.create(
            username=cls.validUsername,
            email="aswinshenoy65@gmail.com"
        )
        cls.user.set_password("W3@kP@$$w0rb!")
        cls.user.save()

        class Context:
            def __init__(self, userID=None):
                self.userID = userID

        cls.unAuthContext = Context()

        cls.authenticateUserMutation = """
        mutation ($email: String, $username: String, $password: String!) {
          authenticateUser(email: $email, username: $username, password: $password) {
            success
            user {
              id
              username
            }
          }
        }
        """

    def test_successful_authentication_using_email_pass(self):
        result = schema.execute(
            self.authenticateUserMutation,
            variables={
                "email": self.validEmail,
                "password": self.validPassword
            },
            context=self.unAuthContext
        )
        assert not result.errors
        expectedResults = {
            "authenticateUser": {
                "success": True,
                "user": {
                    "id": "1",
                    "username": self.validUsername
                }
            }
        }
        assert result.data == expectedResults

    def test_successful_authentication_using_username_pass(self):
        result = schema.execute(
            self.authenticateUserMutation,
            variables={
                "username": self.validUsername,
                "password": self.validPassword
            },
            context=self.unAuthContext
        )
        assert not result.errors
        expectedResults = {
            "authenticateUser": {
                "success": True,
                "user": {
                    "id": "1",
                    "username": self.validUsername
                }
            }
        }
        assert result.data == expectedResults

    def test_failed_authentication_using_email_pass(self):
        result = schema.execute(
            self.authenticateUserMutation,
            variables={
                "email": self.validEmail,
                "password": "invalidPass"
            },
            context=self.unAuthContext
        )
        assert result.errors

    def test_failed_authentication_using_username_pass(self):
        result = schema.execute(
            self.authenticateUserMutation,
            variables={
                "username": "ssss",
                "password": "invalidPass"
            },
            context=self.unAuthContext
        )
        assert result.errors
