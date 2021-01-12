# Chowkidar
### JWT Authentication for Django Graphene
[![license](https://img.shields.io/github/license/aswinshenoy/chowkidar.svg)](LICENSE)
[![npm](https://img.shields.io/pypi/v/chowkidar-graphene)](https://pypi.org/project/chowkidar-graphene/)

An JWT-based authentication package for Django [Graphene](https://github.com/graphql-python/graphene) GraphQL APIs.

### Features
* Support for [Graphene](https://github.com/graphql-python/graphene) GraphQL APIs
* Token & Refresh Token based JWT Authentication
* Tokens stored as server-side cookie
* Support for restricting 1 device / 1 login for a user
* Support for logging IP & User-Agent of user
* Ability to Auto-Refresh JWT Token if the Refresh Token Exists
* Support for Social Auth with [social-app-django](https://github.com/python-social-auth/social-app-django)
* Support for Authenticated GraphQL Subscriptions with Django Channels
* Support for file uploads adhering to [GraphQL Multipart Request Spec](https://github.com/jaydenseric/graphql-multipart-request-spec)
* Get current logged-in user instance in info.context of resolvers

### Installation
Install the package -
```bash
pip install chowkidar-graphene
```
Add `chowkidar` to `INSTALLED_APPS` and run migrations to apply required db changes to the database.

In `urls.py`, replace the GraphQLView coming from the Ariadne with the one from this package
```python3
from chowkidar.graphql import GraphQLView
```
```python3
urlpatterns = [
    path('admin/', admin.site.urls),
    path('graphql/', GraphQLView.as_view(schema=schema), name='graphql'),
    ...
]
```

Add the package to Graphene Middleware in `settings.py`
```python
GRAPHENE = {
    'SCHEMA': 'framework.graphql.schema.schema',
    'MIDDLEWARE': [
        'chowkidar.auth.ChowkidarAuthMiddleware',
        'graphene_django.debug.DjangoDebugMiddleware'
    ],
}
```

Add the mutations to your schema
```python3
from chowkidar.graphql import AuthMutations, SocialAuthMutations

class Mutation(
    AuthMutations,
    SocialAuthMutations,
    ...
):
    pass

schema = graphene.Schema(mutation=Mutation, query=Query)
```

### Auth Decorators
Chowkidar supports 2 decorators that you can use in your API resolvers
```python3
from chowkidar.graphql import login_required, fingerprint_required, resolve_user

@login_required
def resolve_field(self, info, sport=None, state=None, count=5, after=None):
    userID: str = info.context.userID
    some_function()

@fingerprint_required
def resolve_field(self, info, sport=None, state=None, count=5, after=None):
    refreshToken = info.context.refreshToken
    userID: str = info.context.userID
    some_function()


@resolve_user()
def mutate(self, info):
    user: User = info.context.user
    userID: str = info.context.userID
    some_update()
```

1. **`@login_required`** - checks if user is authenticated, and passes down his/her userID at 
info.context.userID. Does not hit the db.

2.  **`@fingerprint_required`** - checks the refresh token of the user against db after validating its
fingerprint and returns info.context.userID & info.context.refreshToken

3. **`@resolve_user`** - checks if user is authenticated, and passes down his/her instance at info.context.user 
as well as his ID at info.context.userID. Hits the db to get the user instance.

Both of these decorators, when wrapped around a query/mutation/type resolver, ensures that only logged-in users 
can access it, when it is an unauthenticated request it shall 
throw exception - `PermissionDenied(message='User not authenticated', code='AUTHENTICATION_REQUIRED')`

### GraphQL Subscriptions with Django Channels

In your `routing.py` -
```python3 
from django.urls import path

from channels.routing import URLRouter, ProtocolTypeRouter

from chowkidar.graphql import AuthenticatedChannel

from .graphql.schema import schema # replace this with your schema

application = ProtocolTypeRouter(
    {
        "websocket": (
            URLRouter(
                [path("ws/", AuthenticatedChannel(schema, debug=True))]
            )
        ),
    }
)
```

Doing this, you will get the logged-in user instance at `info.context['user']`,
which you can handle as per your wish. You can also use the `@login_required` decorator
that comes along with this package.

### Mutations
Our Mutations (& GraphQL APIs) for auth may be not implemented according to basic graphql standards, 
primarily because of technicalities involved in doing certain procedures (like setting up the cookie).
 
**Login a user**

- `success`, and `id` + `username` of the user are compulsory for the mutations to work.

```graphql
mutation {
  authenticateUser(email: "aswinshenoy65@gmail.com", password: "<MY_PASSWORD>") {
    success
    user {
      id
      username
    }
  }
}
```

* **note**: `user { id username }` is a required selection for the authentication to happen. 
Without id & username fields, it will not resolve & return 500.

You may use `username` variable to send email as well. However, you cannot do vice-versa.
```graphql
mutation {
  authenticateUser(username: "aswinshenoy65@gmail.com", password: "<MY_PASSWORD>") {
    success
    user {
      id
      username
    }
  }
}

```

on success the following is returned, and 2 cookies (REFRESH_TOKEN & ACCESS_TOKEN) are set -
```json
{
  "data": {
    "authenticateUser": {
      "success": true,
      "user": {
        "id": "2441264196336223233",
        "username": "aswinshenoy"
      },
      "refreshExpiresIn": "2020-11-21T01:21:51.848Z"
    }
  }
}
```

**Social Auth**

* mostly same as `authenticateUser` but sends `accessToken`+`provider` instead of `email/username` + `password`

```graphql
mutation {
  socialAuth(accessToken: "<SOME TOKEN>", provider: "<SOCIAL_AUTH_PROVIDER>"){
    success
    user
    {
      id
      username
    }
  }
}
```

**Logout a user**

This is required since the cookies are server-side, and needs to be removed.

```graphql
mutation {
  logoutUser
}
```

**View sessions of a user**
```graphql
{
  mySessions{
    isActive
    token
    userAgent
    ip
    issued
    revoked
  }
}
```

**Revoke Token**
Revoke a given refresh token of the user
```graphql
mutation ($token: String!){
  revokeToken(token: $token)
}
```

**Revoke Other Tokens**
Revoke all tokens except the current token. Useful to logout user from all other devices

```graphql
mutation {
  revokeOtherTokens
}
```

#### Available Settings
The following are the settings variables for the plugin to be defined in your project's `settings.py`. 
All the setting variables along with their defaults values are listed below -

```python

JWT_SECRET_KEY = settings.SECRET_KEY
JWT_PUBLIC_KEY = None
JWT_PRIVATE_KEY = None
JWT_REFRESH_TOKEN_N_BYTES = 20
JWT_ALGORITHM = HS256
JWT_EXPIRATION_DELTA = timedelta(seconds=60)
JWT_REFRESH_TOKEN_EXPIRATION_DELTA = timedelta(seconds=60 * 60 * 24 * 7)
JWT_LEEWAY = 0
JWT_ISSUER = None

# function with spec (user: User): bool, defaults to True
ALLOW_USER_TO_LOGIN_ON_AUTH = 'chowkidar.auth.rules.check_if_user_is_allowed_to_login'
# function with spec (user: User): bool, defaults to False
REVOKE_OTHER_TOKENS_ON_AUTH_FOR_USER = 'chowkidar.auth.rules.check_if_other_tokens_need_to_be_revoked'

UPDATE_USER_LAST_LOGIN_ON_AUTH = True
UPDATE_USER_LAST_LOGIN_ON_REFRESH = True
USER_GRAPHENE_OBJECT = 'user.graphql.types.user.PersonalProfile'

LOG_USER_IP_IN_REFRESH_TOKEN = True
LOG_USER_AGENT_IN_REFRESH_TOKEN = True

```

#### FAQ

**1. How to know whether RefreshToken has expired in the frontend?**

0. When you do login using the API, we send back `refreshExpiresIn` on success. 
1. Create a local cookie with expire time set to this `refreshExpiresIn`, with some value. 
2. Before you send any authentication required requests (or before you open a auth required page), check whether this cookie exists.

**2. Do I need to refresh the access token?**

No, as long as you send both refresh token and the access token in the request (which you should automatically, 
since its a server side cookie) the server will perform the refresh if a valid refresh token exists either when 
approaching expiry of access token, or when having an expired access token. In both cases, the actual query shall 
also be properly resolved and not failed. :) 

### Contributing
Contributions are welcome! Feel free to open issues, and work on PRs to fix them.

#### Building & Publishing the package
```bash
    python setup.py sdist
    twine upload dist/*
```

### Credits
This project is heavily inspired by `django-graphql-jwt` & `django-graphql-social-auth` by flavors, 
and is loosely forked from its implementation. 

### License
This project is licensed under the GNU General Public License V3. 