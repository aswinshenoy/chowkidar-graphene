# Chowkidar
### JWT Authentication for Django Graphene
[![npm](https://img.shields.io/pypi/v/chowkidar-graphene)](https://pypi.org/project/chowkidar-graphene/)
[![license](https://img.shields.io/github/license/aswinshenoy/chowkidar.svg)](LICENSE)

An JWT-based authentication package for Django [Graphene](https://github.com/graphql-python/graphene) GraphQL APIs.

### Features
* Out-of-the-box support for [Graphene](https://github.com/graphql-python/graphene) GraphQL APIs
* Token & Refresh Token based JWT Authentication
* Tokens stored as server-side cookie
* Ability to Auto-Refresh JWT Token if the Refresh Token Exists
* Support for Social Auth with `social-app-django`
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
from chowkidar.graphql import login_required, resolve_user

@login_required
def resolve_field(self, info, sport=None, state=None, count=5, after=None):
    userID: str = info.context.userID
    some_function()

@resolve_user()
def mutate(self, info):
    user: User = info.context.user
    some_update()
```

1. **`@login_required`** - checks if user is authenticated, and passes down his/her userID at 
info.context.userID. Does not hit the db.

2. **`@resolve_user`** - checks if user is authenticated, and passes down his/her instance at info.context.user 
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
      "payload": {
        "userID": "2441264196336223233",
        "username": "aswinshenoy",
        "origIat": 1605316911.841719,
        "iat": 1605316911,
        "exp": 1605317211
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

#### FAQ

**1. How to know whether RefreshToken has expired?**

0. When you do login using the API, we send back `refreshExpiresIn` on success. 
1. Create a local cookie with expire time set to this `refreshExpiresIn`, with some value. 
2. Before you send any authentication required requests (or before you open a auth required page), check whether this cookie exists.

**2. Do I need to refresh the access token?**

No, as long as you send both refresh token and the access token in the request (which you should automatically, 
since its a server side cookie) the server will perform the refresh if a valid refresh token exists either when 
approaching expiry of access token, or when having an expired access token. In both cases, the actual query shall 
also be properly resolved and not failed. :) 

### Credits
This project is heavily inspired by `django-graphql-jwt` & `django-graphql-social-auth` by flavors, 
and is loosely forked from its implementation. 

### License
This project is licensed under the GNU General Public License V3. 