# -*- coding: utf-8 -*-
import json
import math
import logging
import requests
import werkzeug

from odoo import http, _, exceptions
from odoo.http import request

from .serializers import Serializer
from .exceptions import QueryFormatError

_logger = logging.getLogger(__name__)


def error_response(error, msg):
    return {
        "jsonrpc": "2.0",
        "id": None,
        "error": {
            "code": 200,
            "message": msg,
            "data": {
                "name": str(error),
                "debug": "",
                "message": msg,
                "arguments": list(error.args),
                "exception_type": type(error).__name__
            }
        }
    }


class OdooAPI(http.Controller):
    @http.route(
        '/getsession/',
        type='http', auth='user', methods=["GET"], csrf=True)
    def getsessionGet(self, **args):
        if "redirectUrl" not in args:
            return http.Response(
                json.dumps("Bad request"),
                status=400,
                mimetype='application/json'
            )

        return http.request.render("8x8-integration.auth_page", {
          'redirectUrl' : args["redirectUrl"]
        })

    @http.route(
        '/getsession/',
        type='http', auth='user', methods=["POST"], csrf=True)
    def getsessionPost(self, **args):
        if "redirect" not in args:
            return http.Response(
                json.dumps("Bad request"),
                status=400,
                mimetype='application/json'
            )

        if args["redirect"]:
            urlData = args["redirect"] + '&code=' + request.session.sid
        else:
            urlData = '/'

        return werkzeug.utils.redirect(urlData, 301)

    @http.route(
        '/auth/',
        type='json', auth='none', methods=["POST"], csrf=False)
    def authenticate(self, *args, **post):
        try:
            login = post["login"]
        except KeyError:
            raise exceptions.AccessDenied(message='`login` is required.')

        try:
            password = post["password"]
        except KeyError:
            raise exceptions.AccessDenied(message='`password` is required.')

        try:
            db = post["db"]
        except KeyError:
            raise exceptions.AccessDenied(message='`db` is required.')

        url_root = request.httprequest.url_root
        AUTH_URL = f"{url_root}web/session/authenticate/"

        headers = {'Content-type': 'application/json'}

        data = {
            "jsonrpc": "2.0",
            "params": {
                "login": login,
                "password": password,
                "db": db
            }
        }

        res = requests.post(
            AUTH_URL,
            data=json.dumps(data),
            headers=headers
        )

        try:
            session_id = res.cookies["session_id"]
            user = json.loads(res.text)
            user["result"]["session_id"] = session_id
        except Exception:
            return "Invalid credentials."
        return user["result"]

    @http.route(
        '/object/<string:model>/<string:function>',
        type='json', auth='user', methods=["POST"], csrf=False)
    def call_model_function(self, model, function, **post):
        args = []
        kwargs = {}
        if "args" in post:
            args = post["args"]
        if "kwargs" in post:
            kwargs = post["kwargs"]
        model = request.env[model]
        result = getattr(model, function)(*args, **kwargs)
        return result

    @http.route(
        '/object/<string:model>/<int:rec_id>/<string:function>',
        type='json', auth='user', methods=["POST"], csrf=False)
    def call_obj_function(self, model, rec_id, function, **post):
        args = []
        kwargs = {}
        if "args" in post:
            args = post["args"]
        if "kwargs" in post:
            kwargs = post["kwargs"]
        obj = request.env[model].browse(rec_id).ensure_one()
        result = getattr(obj, function)(*args, **kwargs)
        return result

    @http.route(
        '/api/<string:model>',
        type='http', auth='user', methods=['GET'], csrf=True)
    def get_model_data(self, model, **params):
        try:
            records = request.env[model].search([])
        except KeyError as e:
            msg = "The model `%s` does not exist." % model
            res = error_response(e, msg)
            return http.Response(
                json.dumps(res),
                status=200,
                mimetype='application/json'
            )

        if "query" in params:
            query = params["query"]
        else:
            query = "{*}"

        if "order" in params:
            orders = json.loads(params["order"])
        else:
            orders = ""

        if "filter" in params:
            filters = json.loads(params["filter"])
            records = request.env[model].search(filters, order=orders)

        prev_page = None
        next_page = None
        total_page_number = 1
        current_page = 1

        if "page_size" in params:
            page_size = int(params["page_size"])
            count = len(records)
            total_page_number = math.ceil(count/page_size)

            if "page" in params:
                current_page = int(params["page"])
            else:
                current_page = 1  # Default page Number
            start = page_size*(current_page-1)
            stop = current_page*page_size
            records = records[start:stop]
            next_page = current_page+1 \
                if 0 < current_page + 1 <= total_page_number \
                else None
            prev_page = current_page-1 \
                if 0 < current_page - 1 <= total_page_number \
                else None

        if "limit" in params:
            limit = int(params["limit"])
            records = records[0:limit]

        try:
            serializer = Serializer(records, query, many=True)
            _logger.error(records)
            data = serializer.data
        except (SyntaxError, QueryFormatError) as e:
            res = error_response(e, e.msg)
            return http.Response(
                json.dumps(res),
                status=200,
                mimetype='application/json'
            )

        res = {
            "count": len(records),
            "prev": prev_page,
            "current": current_page,
            "next": next_page,
            "total_pages": total_page_number,
            "result": data
        }
        return http.Response(
            json.dumps(res),
            status=200,
            mimetype='application/json'
        )

    @http.route(
        '/api/<string:model>/<int:rec_id>',
        type='http', auth='user', methods=['GET'], csrf=False)
    def get_model_rec(self, model, rec_id, **params):
        try:
            records = request.env[model].search([])
        except KeyError as e:
            msg = "The model `%s` does not exist." % model
            res = error_response(e, msg)
            return http.Response(
                json.dumps(res),
                status=200,
                mimetype='application/json'
            )

        if "query" in params:
            query = params["query"]
        else:
            query = "{*}"

        # TODO: Handle the error raised by `ensure_one`
        record = records.browse(rec_id).ensure_one()

        try:
            serializer = Serializer(record, query)
            data = serializer.data
        except (SyntaxError, QueryFormatError) as e:
            res = error_response(e, e.msg)
            return http.Response(
                json.dumps(res),
                status=200,
                mimetype='application/json'
            )

        return http.Response(
            json.dumps(data),
            status=200,
            mimetype='application/json'
        )

    @http.route(
        '/api/<string:model>/',
        type='json', auth="user", methods=['POST'], csrf=False)
    def post_model_data(self, model, **post):
        try:
            data = post['data']
        except KeyError:
            msg = "`data` parameter is not found on POST request body"
            raise exceptions.ValidationError(msg)

        try:
            model_to_post = request.env[model]
        except KeyError:
            msg = "The model `%s` does not exist." % model
            raise exceptions.ValidationError(msg)

        # TODO: Handle data validation

        if "context" in post:
            context = post["context"]
            record = model_to_post.with_context(**context).create(data)
        else:
            record = model_to_post.create(data)
        return record.id

    # This is for single record update
    @http.route(
        '/api/<string:model>/<int:rec_id>/',
        type='json', auth="user", methods=['PUT'], csrf=False)
    def put_model_record(self, model, rec_id, **post):
        try:
            data = post['data']
        except KeyError:
            msg = "`data` parameter is not found on PUT request body"
            raise exceptions.ValidationError(msg)

        try:
            model_to_put = request.env[model]
        except KeyError:
            msg = "The model `%s` does not exist." % model
            raise exceptions.ValidationError(msg)

        if "context" in post:
            # TODO: Handle error raised by `ensure_one`
            rec = model_to_put.with_context(**post["context"])\
                .browse(rec_id).ensure_one()
        else:
            rec = model_to_put.browse(rec_id).ensure_one()

        # TODO: Handle data validation
        for field in data:
            if isinstance(data[field], dict):
                operations = []
                for operation in data[field]:
                    if operation == "push":
                        operations.extend(
                            (4, rec_id, _)
                            for rec_id
                            in data[field].get("push")
                        )
                    elif operation == "pop":
                        operations.extend(
                            (3, rec_id, _)
                            for rec_id
                            in data[field].get("pop")
                        )
                    elif operation == "delete":
                        operations.extend(
                            (2, rec_id, _)
                            for rec_id
                            in data[field].get("delete")
                        )
                    else:
                        data[field].pop(operation)  # Invalid operation

                data[field] = operations
            elif isinstance(data[field], list):
                data[field] = [(6, _, data[field])]  # Replace operation
            else:
                pass

        try:
            return rec.write(data)
        except Exception as e:
            # TODO: Return error message(e.msg) on a response
            return False

    # This is for bulk update
    @http.route(
        '/api/<string:model>/',
        type='json', auth="user", methods=['PUT'], csrf=False)
    def put_model_records(self, model, **post):
        try:
            data = post['data']
        except KeyError:
            msg = "`data` parameter is not found on PUT request body"
            raise exceptions.ValidationError(msg)

        try:
            model_to_put = request.env[model]
        except KeyError:
            msg = "The model `%s` does not exist." % model
            raise exceptions.ValidationError(msg)

        # TODO: Handle errors on filter
        filters = post["filter"]

        if "context" in post:
            recs = model_to_put.with_context(**post["context"])\
                .search(filters)
        else:
            recs = model_to_put.search(filters)

        # TODO: Handle data validation
        for field in data:
            if isinstance(data[field], dict):
                operations = []
                for operation in data[field]:
                    if operation == "push":
                        operations.extend(
                            (4, rec_id, _)
                            for rec_id
                            in data[field].get("push")
                        )
                    elif operation == "pop":
                        operations.extend(
                            (3, rec_id, _)
                            for rec_id
                            in data[field].get("pop")
                        )
                    elif operation == "delete":
                        operations.extend(
                            (2, rec_id, _)
                            for rec_id in
                            data[field].get("delete")
                        )
                    else:
                        pass  # Invalid operation

                data[field] = operations
            elif isinstance(data[field], list):
                data[field] = [(6, _, data[field])]  # Replace operation
            else:
                pass

        if recs.exists():
            try:
                return recs.write(data)
            except Exception as e:
                # TODO: Return error message(e.msg) on a response
                return False
        else:
            # No records to update
            return True

    # This is for deleting one record
    @http.route(
        '/api/<string:model>/<int:rec_id>/',
        type='http', auth="user", methods=['DELETE'], csrf=False)
    def delete_model_record(self, model,  rec_id, **post):
        try:
            model_to_del_rec = request.env[model]
        except KeyError as e:
            msg = "The model `%s` does not exist." % model
            res = error_response(e, msg)
            return http.Response(
                json.dumps(res),
                status=200,
                mimetype='application/json'
            )

        # TODO: Handle error raised by `ensure_one`
        rec = model_to_del_rec.browse(rec_id).ensure_one()

        try:
            is_deleted = rec.unlink()
            res = {
                "result": is_deleted
            }
            return http.Response(
                json.dumps(res),
                status=200,
                mimetype='application/json'
            )
        except Exception as e:
            res = error_response(e, str(e))
            return http.Response(
                json.dumps(res),
                status=200,
                mimetype='application/json'
            )

    # This is for bulk deletion
    @http.route(
        '/api/<string:model>/',
        type='http', auth="user", methods=['DELETE'], csrf=False)
    def delete_model_records(self, model, **post):
        filters = json.loads(post["filter"])

        try:
            model_to_del_rec = request.env[model]
        except KeyError as e:
            msg = "The model `%s` does not exist." % model
            res = error_response(e, msg)
            return http.Response(
                json.dumps(res),
                status=200,
                mimetype='application/json'
            )

        # TODO: Handle error raised by `filters`
        recs = model_to_del_rec.search(filters)

        try:
            is_deleted = recs.unlink()
            res = {
                "result": is_deleted
            }
            return http.Response(
                json.dumps(res),
                status=200,
                mimetype='application/json'
            )
        except Exception as e:
            res = error_response(e, str(e))
            return http.Response(
                json.dumps(res),
                status=200,
                mimetype='application/json'
            )

    @http.route(
        '/api/<string:model>/<int:rec_id>/<string:field>',
        type='http', auth="user", methods=['GET'], csrf=False)
    def get_binary_record(self, model,  rec_id, field, **post):
        try:
            request.env[model]
        except KeyError as e:
            msg = "The model `%s` does not exist." % model
            res = error_response(e, msg)
            return http.Response(
                json.dumps(res),
                status=200,
                mimetype='application/json'
            )

        rec = request.env[model].browse(rec_id).ensure_one()
        if rec.exists():
            src = getattr(rec, field).decode("utf-8")
        else:
            src = False
        return http.Response(
            src
        )

    @http.route(
        '/api8x8/phonenumber/<string:model>',
        type='json', auth='user', methods=['POST'], csrf=False)
    def get_model_by_phonenumber_data(self, model, **post):
        try:
            records = request.env[model].search([])
        except KeyError as e:
            return http.Response(
                json.dumps("The model `%s` does not exist." % model),
                status=400,
                mimetype='application/json'
            )

        if "query" in post:
            query = post["query"]
        else:
            query = "{*}"

        if "order" in post:
            orders = post["order"]
        else:
            orders = ""

        if "filter" in post:
            filters = json.loads(post["filter"])
        else:
            filters = []

        if "phone" in post:
            phones = json.loads(post["phone"])
        else:
            phones = []

        tableName = model.replace('.', '_')

        whereQuery = []
        for field, operator, value in phones:
            if (value.isnumeric() == False):
                return http.Response(
                    json.dumps("The filter field `%s` is not numeric." % field),
                    status=400,
                    mimetype='application/json'
                )

            operators = ['contains', 'is']
            strOperators = '`, `'.join(operators)
            if operator not in operators:
                return http.Response(
                    json.dumps("The operator for `%s` is not `%s`." % (field, strOperators)),
                    status=400,
                    mimetype='application/json'
                )

            if operator == 'contains':
                value = '%{}%'.format(value)
                operator = 'like'
            elif operator == 'is':
                operator = '='

            whereQuery.append("regexp_replace({}, '[^0-9]+', '', 'g') {} '{}'".format(field, operator, value))

        if len(whereQuery):
            where = ' OR '.join(whereQuery)
            rawQuery = "SELECT id FROM {} WHERE {}".format(tableName, where)
            request._cr.execute(rawQuery)
            found = request._cr.fetchall()
            filters.append(['id', 'in', found])

        records = request.env[model].search(filters, order=orders)

        prev_page = None
        next_page = None
        total_page_number = 1
        current_page = 1

        if "page_size" in post:
            page_size = int(post["page_size"])
            count = len(records)
            total_page_number = math.ceil(count/page_size)

            if "page" in post:
                current_page = int(post["page"])
            else:
                current_page = 1  # Default page Number
            start = page_size*(current_page-1)
            stop = current_page*page_size
            records = records[start:stop]
            next_page = current_page+1 \
                if 0 < current_page + 1 <= total_page_number \
                else None
            prev_page = current_page-1 \
                if 0 < current_page - 1 <= total_page_number \
                else None

        if "limit" in post:
            limit = int(post["limit"])
            records = records[0:limit]

        try:
            serializer = Serializer(records, query, many=True)
            data = serializer.data
        except (SyntaxError, QueryFormatError) as e:
            # res = error_response(e, e.msg)
            return http.Response(
                json.dumps("Json parsing error"),
                status=400,
                mimetype='application/json'
            )

        res = {
            "count": len(records),
            "prev": prev_page,
            "current": current_page,
            "next": next_page,
            "total_pages": total_page_number,
            "result": data,
            "testrecords": records
        }

        return res
