import json

from tornado import gen
from tornado.web import HTTPError

from app.client.features.base import BaseFeature


class JsonFeature(BaseFeature):

    @gen.engine
    def __call__(self, request, callback):
        if request.method == "POST" or request.method == "PUT":
            request.headers['content-type'] = "application/json"

        request.headers['accept'] = "application/json"

        response = yield gen.Task(self.next_feature, request)
        # TODO: It doesn't look like this try/except works :/
        try:
            if response.body is not None and response.body != "":
                response.body = json.loads(response.body)
        except:
            raise HTTPError(500, "Unable to parse response body as json")

        callback(response)
