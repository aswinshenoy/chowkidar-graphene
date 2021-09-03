import json
from typing import Union

from django.shortcuts import render
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import ensure_csrf_cookie
from django.http.response import HttpResponseNotAllowed

from graphql.error import GraphQLSyntaxError
from graphql.error import GraphQLError
from graphql.error.located_error import GraphQLLocatedError
from graphene_django.views import GraphQLView as BaseGraphQLView

from graphene.utils.str_converters import to_snake_case, to_camel_case

from .files import place_files_in_operations
from ..auth import respond_handling_authentication
from ..settings import PROTECT_GRAPHQL


class ResponseError(Exception):
    def __init__(self, message, code=None, params=None):
        super().__init__(message)
        self.message = str(message)
        self.code = code
        self.params = params


def to_kebab_case(s):
    return to_snake_case(s).replace('_', '-')


def encode_key(k):
    return to_camel_case(k)


def dict_key_to_camel_case(d: dict):
    return dict((encode_key(k), v) for k, v in d.items())


class HttpError(Exception):
    def __init__(self, response, message=None, *args, **kwargs):
        self.response = response
        self.message = message = message or response.content.decode()
        super(HttpError, self).__init__(message, *args, **kwargs)


class GraphQLView(BaseGraphQLView):
    schema = None
    graphiql = False
    executor = None
    backend = None
    middleware = None
    root_value = None
    pretty = False
    batch = False
    subscription_path = None

    @method_decorator(ensure_csrf_cookie)
    def dispatch(self, request, *args, **kwargs):
        if request.method.lower() not in ("get", "post", "options"):
            raise HttpError(
                HttpResponseNotAllowed(
                    ["GET", "POST", "OPTIONS"], "Only supports GET, POST and OPTIONS requests."
                )
            )
        allowGraphiQL = self.graphiql and not PROTECT_GRAPHQL
        if request and request.user and request.user.is_staff:
            allowGraphiQL = True
        if allowGraphiQL:
            data = self.parse_body(request)
            if self.can_display_graphiql(request, data):
                return render(request, "graphiql/graphiql.html")
        if PROTECT_GRAPHQL and request.method.lower() not in "post":
            raise HttpError(
                HttpResponseNotAllowed(
                    ["POST"], "Only supports POST requests."
                )
            )
        try:
            if self.batch:
                raise HttpError(
                    HttpResponseNotAllowed("Batch queries not supported")
                )
            data = self.parse_body(request)
            result, status_code = self.get_response(request, data)
            return respond_handling_authentication(status_code=status_code, result=json.loads(result), request=request)
        except HttpError as e:
            return respond_handling_authentication(
                status_code=e.response.code,
                result={"errors": [self.format_error(e)]},
                request=request
            )

    def parse_body(self, request):
        """Handle multipart request spec for multipart/form-data"""
        content_type = self.get_content_type(request)
        if content_type == 'multipart/form-data':
            operations = json.loads(request.POST.get('operations', '{}'))
            files_map = json.loads(request.POST.get('map', '{}'))
            return place_files_in_operations(
                operations,
                files_map,
                request.FILES
            )
        return super(GraphQLView, self).parse_body(request)

    @staticmethod
    def encode_params(params):
        if params is None:
            return None
        return dict_key_to_camel_case(params)

    @staticmethod
    def get_locations(error):
        if error.locations:
            locations = []
            for loc in error.locations:
                locations.append({"line": loc.line, "column": loc.column})
            return locations

    def format_response_error(self, error: Union[ResponseError, Exception]):
        returnObj = {}
        if hasattr(error, 'message') and error.message:
            returnObj['message'] = error.message
        if hasattr(error, 'code') and error.code:
            returnObj['code'] = error.code
        if hasattr(error, 'params') and error.params:
            returnObj['params'] = self.encode_params(error.params)
        return returnObj

    def format_error(self, error):
        if isinstance(error, GraphQLLocatedError):
            return self.format_response_error(error.original_error)
        if isinstance(error, GraphQLSyntaxError):
            if PROTECT_GRAPHQL:
                return {"message": "Invalid Request", "code": "SYNTAX_ERROR"}
            return {
                "message": error.message,
                "location": self.get_locations(error),
                "code": "GRAPHQL_SYNTAX_ERROR"
            }
        if isinstance(error, GraphQLError):
            if PROTECT_GRAPHQL:
                return {"message": "This request could not be processed", "code": "BAD_REQUEST"}
            return {
                "message": error.message,
                "location": self.get_locations(error),
                "code": "BAD_REQUEST"
            }
        return {
            "code": "INTERNAL_SERVER_ERROR",
            "message": "Something went wrong while handling this request."
        }


__all__ = [
    'GraphQLView'
]
