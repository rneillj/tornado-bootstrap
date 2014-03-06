#!/usr/bin/env python
""" Base Transformer """

from app.config import config


class BaseTransformer(object):

    def transform_data(self, data, *args, **kwargs):
        """
        Abstract method. Must be implemented as a concrete method by the
        extending class.
        """
        raise NotImplementedError("This is an abstract method. It must be "
                                  "implemented as a concrete method in an "
                                  "inheriting class.")

    def transform_list(self, data_list, *args):
        return [self.transform_data(d, *args) for d in data_list]

    def _add_name(self, data, data_type, **kwargs):
        for d in data.get(data_type, []):
            if not config['feature_toggle']['future_api']:
                if not isinstance(d, dict):
                    d = {'id': d}
            for h in kwargs.get(data_type, []):
                if not isinstance(h, dict):
                    h = {'id': h}
                link_id = None
                if 'link' in h and 'id' in h['link']:
                    link_id = h['link']['id']
                h_id = h.get('id', h.get('device_id', link_id))
                if str(d['id']) == str(h_id):
                    d['name'] = h.get('name', '')
                    d['name'] = self._format_name(d)
                    d['uuid'] = h.get('uuid', '')
                    d['ipAddress'] = h.get('ip', '')
                    d['datacenter'] = h.get('datacenter', '')
                    d['datacenterAbbr'] = h.get('datacenter_symbol', '')

            for k in ['legacy_href', 'rel']:
                if k in d:
                    del d[k]

        return data[data_type]

    def _add_parent(self, device_types, **kwargs):
        """ Grab the specific data required for returning parent info """

        parent_data = {}

        for parent in kwargs.get("devices", []):
            if parent["device_type"] in device_types:
                parent_data = {
                    "id": parent.get(
                        "legacy_device_number", parent.get("device_id", "")),
                    "name": self._format_name(parent),
                    "ipAddress": parent.get("ip", ""),
                    "datacenter": parent.get("datacenter", ""),
                    "datacenterAbbr": parent.get("datacenter_symbol", ""),
                    "uuid": parent.get("uuid", "")
                }
                break

        return parent_data

    def _format_name(self, data):
        data['id'] = data.get('legacy_device_number', data.get('id'))

        if 'id' not in data or 'name' not in data:
            return ''

        to_replace = '{0}-'.format(data['id'])
        return (data['name'] or '').replace(to_replace, '')

    def _format_account_link(self, id):
        return '{0}/py/core/#/account/{1}'.format(
            config['core']['endpoint'],
            id
        )
