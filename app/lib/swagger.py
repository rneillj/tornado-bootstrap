#!/usr/bin/env python
import re

from tornado.web import URLSpec
from app.config import config


def list_modules(tornado_routes):
    """ List all of the modules we have defined for the swagger load page """
    modules = {"defaults": {"path": "/everything_else"}}

    for route in tornado_routes:
        if type(route) != URLSpec or route.module is None:
            continue
        modules[route.module] = {"path": "/" + route.module}

    return [x for x in modules.values()]


def api_docs(tornado_routes, module):

    routes = []  # List of all routes
    models = {}  # Dict of datatypes (incoming and outgoing)

    for route in tornado_routes:
        # Ignore routes that are not URLSpecs or belong to different modules
        if type(route) != URLSpec or route.module != module:
            continue

        # By default, we have an empty handler with no operations
        handler = {
            "path": route.name,
            "operations": []
        }

        # For each relevant verb, lets build the docs for it
        for verb in ["get", "put", "post", "delete"]:

            method = getattr(route.handler_class, verb)

            # If the method doesn't have a doc string, ignore it
            if getattr(method, "__doc__"):

                # Create the base operation
                operation = get_operation(verb, method)
                set_request_body(operation, models, method)
                set_url_params(operation, route, method)
                set_possible_responses(operation, method)
                set_response_type(operation, models, method)

                handler['operations'].append(operation)

        # Append the handler to the list of routes
        routes.append(handler)

    return {
        "apis": routes,
        "apiVersion": config['api_version'],
        "swaggerVersion": 1.0,
        "resourcePath": "/v1",
        "basePath": config['swagger']['endpoint'],
        "models": models
    }


def get_operation(verb, method):
    """
    Given a method, get the swagger operation
    """

    split = getattr(method, "__doc__").split("\n\n", 1)
    # The first line of the doc string is the summary
    summary = split[0].strip()
    # If there is more than the first line, that is the notes
    notes = split[1].strip() if(len(split) == 2) else summary

    return {
        "method": verb.upper(),  # GET/PUT/POST/DELETE
        "summary": summary,  # One line description of the api call
        "notes": notes,  # Rest of the description
        "produces": ["application/json"],  # We only ever serve JSON
        "type": "void",  # By default, methods return nothing
        "parameters": [],  # By default, we require nothing
        "nickname": "",  # This field intentionally left blank
        "responseMessages": []  # We will fill this in later
    }


def set_request_body(operation, models, method):
    """
    If there is a schema for this method, we need to set the operation
    body parameter, create the model for the request body, and add a
    possible 400 response code
    """

    schema = getattr(method, "schema_name", None)
    if schema is None:
        return

    # If there is JSON, it has potential to be messed up
    operation['responseMessages'].append({
        "code": 400,
        "message": "Malformed JSON or missing required data"
    })

    # We need to add the object to the models dict
    models[schema] = cerberus_to_swagger(
        getattr(method, "validator_schema", ""))

    # Add to the parameters array
    operation['parameters'].append({
        "paramType": "body",
        "name": "JSON Body",
        "description": getattr(method, "example", "No example provided."),
        "type": schema,
        "required": True
    })


def set_url_params(operation, route, method):
    """
    If there are any URL params or query parameters, add them to the
    swagger operation.
    """

    # For each {param} in the url, add it as a require parameter
    for param in re.findall(r'{[a-z]*}', route.name):
        operation['parameters'].append({
            "paramType": "path",
            "name": param[1:-1],
            "type": "string",
            "required": True,
        })

    # Add any query parameters that were defined
    query_params = getattr(method, "query_params", {})
    for param, desc in query_params.items():
        operation['parameters'].append({
            "paramType": "query",
            "name": param,
            "description": desc,
            "type": "string",
            "required": False,
        })


def set_possible_responses(operation, method):
    """
    Generate a list of possible responses. Start with a 200 OK, add a 401
    unauthorized (if necessary), as well as any that are defined explicitly
    """

    # Every route should be able to response with a 200
    operation['responseMessages'].append({"code": 200, "message": "OK"})

    # If the method requires authentication, we have a possible 401 response
    if not getattr(method, "no_auth", False):
        operation['responseMessages'].append({
            "code": 401,
            "message": "You must have a valid token to perform this operation"
        })

    # If the method defined additional response messages, add them
    if getattr(method, "possible_responses", None):
        for response in getattr(method, "possible_responses"):
            operation['responseMessages'].append(response)


def set_response_type(operation, models, method):
    """
    Set the operation response type and add the type to the models list
    """
    response_type = getattr(method, "response_type", None)
    if response_type is None:
        return

    name, model = adapter_to_swagger(response_type)
    models[name] = model
    operation['type'] = name


def adapter_to_swagger(adapter):
    """
    Given an adapter, use the description to generate the
    swagger representation of the response object.
    """
    return (
        "{0}".format(adapter),
        {"properties": adapter.description}
    )


def cerberus_to_swagger(cerberus_schema):
    """
    Given a cerberus schema file, parse it into a swagger representation
    of the request body.
    """
    swagger_model = {
        "required": [],
        "properties": {}
    }
    for key, value in cerberus_schema.items():
        swagger_model['properties'][key] = {
            "type": value["type"]
        }

        if("required" in value and value['required']):
            swagger_model['required'].append(key)
            swagger_model['properties'][key]['required'] = True

    return swagger_model
