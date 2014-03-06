import os
import glob
import yaml

from urlparse import urlsplit, parse_qs
from pkg_resources import resource_filename

from app.config import config


class MockData(object):
    def __init__(self):
        self.mocks = {}

    def add_mock(self, mock):
        if(mock['url'] not in self.mocks):
            self.mocks[mock['url']] = {}
        if(mock['method'] not in self.mocks[mock['url']]):
            self.mocks[mock['url']][mock['method']] = []

        self.mocks[mock['url']][mock['method']] = mock

    def get_response(self, request):
        request_url_split = urlsplit(request.url)  # raw

        request_url = "{0}://{1}{2}".format(
            request_url_split.scheme,
            request_url_split.netloc,
            request_url_split.path
        )
        request_qs = parse_qs(request_url_split.query, keep_blank_values=True)

        request_qs = dict(
            (k, sorted(v[0].split(","))) for k, v in request_qs.items()
        )

        mock = False
        for url, search_mock in self.mocks.items():
            search_url_split = urlsplit(url)
            search_url = "{0}://{1}{2}".format(
                search_url_split.scheme,
                search_url_split.netloc,
                search_url_split.path
            )

            search_qs = parse_qs(
                search_url_split.query,
                keep_blank_values=True
            )
            search_qs = dict(
                (k, sorted(v[0].split(","))) for k, v in search_qs.items()
            )

            if (request_url == search_url and request_qs == search_qs and
                    request.method in search_mock):
                mock = search_mock[request.method]
                break
        else:
            return False

        if not mock:
            return False

        for possible_response in mock['responses']:
            if("body_includes" in possible_response):
                if(possible_response['body_includes'] not in
                        str(request.body)):
                    continue

            return possible_response

        # No matching match found
        return False


def set_mock_data():
    config['mock_data'] = MockData()

    for file_path in glob.glob(os.path.join('mocks', '*', '*.yaml')):
        config['mock_data'].add_mock(yaml.load(open(file_path, 'r')))

    # Add all of the defaults
