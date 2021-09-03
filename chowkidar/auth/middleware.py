from .verify import resolve_user_from_request
from ..settings import PROTECT_GRAPHQL


class ChowkidarAuthMiddleware:

    def resolve(self, next, root, info, **kwargs):
        context = info.context
        if not hasattr(info.context, 'ChowkidarIDResolved'):
            userID = resolve_user_from_request(context)
            info.context.userID = userID
            info.context.ChowkidarIDResolved = True

        if (
            (
                PROTECT_GRAPHQL and
                not (hasattr(info.context, 'user') and info.context.user and info.context.user.is_staff)
            ) and
            (info.field_name == '__schema' or info.field_name == '_debug')
        ):
            from graphql import GraphQLObjectType, GraphQLField, GraphQLSchema, GraphQLString
            # Don't worry, its simply to show a fake query on introspection
            query = GraphQLObjectType(
                "Query", lambda: {
                    "DJANGO_SECRET_KEY": GraphQLField(
                        GraphQLString,
                        description='Get django secret key',
                        resolver=lambda *_: "NOT_SUPPORTED"
                    ),
                }
            )
            info.schema = GraphQLSchema(query=query)
            return next(root, info, **kwargs)
        return next(root, info, **kwargs)


__all__ = [
    'ChowkidarAuthMiddleware'
]
