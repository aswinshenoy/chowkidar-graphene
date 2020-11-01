import json

from django.core.exceptions import FieldError
from django.db import ProgrammingError, DataError, IntegrityError
from django.shortcuts import render
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import ensure_csrf_cookie
from django.http.response import HttpResponseNotAllowed

from graphql.error import GraphQLSyntaxError
from graphql.error import GraphQLError
from graphql.error.located_error import GraphQLLocatedError
from graphene_django.views import GraphQLView as BaseGraphQLView

from graphene.utils.str_converters import to_snake_case, to_camel_case

from framework.graphql.utils import APIException
from .files import place_files_in_operations
from ..auth import respond_handling_authentication
from ..utils import AuthError, PermissionDenied


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
        try:
            if request.method.lower() not in ("get", "post"):
                raise HttpError(
                    HttpResponseNotAllowed(
                        ["GET", "POST"], "GraphQL only supports GET and POST requests."
                    )
                )

            data = self.parse_body(request)
            show_graphiql = self.graphiql and self.can_display_graphiql(request, data)

            if show_graphiql:
                return render(request, "graphiql/graphiql.html")

            if self.batch:
                responses = [self.get_response(request, entry) for entry in data]
                result = "[{}]".format(",".join([response[0] for response in responses]))
                status_code = (responses and max(responses, key=lambda response: response[1])[1] or 200)
            else:
                result, status_code = self.get_response(request, data, show_graphiql)
            return respond_handling_authentication(status_code=status_code, result=json.loads(result), request=request)

        except HttpError as e:
            response = e.response
            response["Content-Type"] = "application/json"
            response.content = self.json_encode(request, {"errors": [self.format_error(e)]})
            return response

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
    def encode_code(code):
        if code is None:
            return None
        return to_kebab_case(code)

    @staticmethod
    def encode_params(params):
        if params is None:
            return None
        return dict_key_to_camel_case(params)

    @staticmethod
    def get_locations(error):
        if error.locations:
            locations = []
            for l in error.locations:
                locations.append({"line": l.line, "column": l.column})
            return locations

    def format_response_error(self, error: ResponseError):
        return {
            'message': error.message,
            'code': self.encode_code(error.code),
            'params': self.encode_params(error.params),
        }

    def format_located_error(self, error):
        if (
            isinstance(error, AuthError) or isinstance(error, PermissionDenied) or isinstance(error, APIException)
        ):
            return {"message": error.message, "code": error.code}
        if isinstance(error, GraphQLLocatedError):
            return self.format_response_error(error)
        if isinstance(error, ResponseError):
            return self.format_response_error(error)
        if isinstance(error, DataError):
            return {"message": error.__repr__(), "code": "DATA_ERROR"}
        if isinstance(error, FieldError):
            return {"message": error.__repr__(), "code": "FIELD_ERROR"}
        if isinstance(error, ProgrammingError):
            return {"message": error.__repr__(), "code": "DB_PROGRAMING_ERROR"}
        if isinstance(error, IntegrityError):
            return {"message": error.__repr__(), "code": "INTEGRITY_ERROR"}
        if isinstance(error, AttributeError):
            return {"message": error.__repr__(), "code": "ATTRIBUTE_ERROR"}
        if isinstance(error, TypeError):
            return {"message": error.__repr__(), "code": "TYPE_ERROR"}
        return self.format_response_error(error)

    def format_error(self, error):
        if isinstance(error, GraphQLLocatedError):
            return self.format_located_error(error.original_error)
        if isinstance(error, GraphQLSyntaxError):
            return {
                "message": error.message,
                "location": self.get_locations(error),
                "code": "GRAPHQL_SYNTAX_ERROR"
            }
        if isinstance(error, GraphQLError):
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
