#!/usr/bin/env python
""" This is the base class from which all logic classes should extend """

import logging


log = logging.getLogger(__name__)


class BaseLogic(object):

    @staticmethod
    def is_vm(data):
        return data['device_type'] in ['vm', 'dedicated_vm']

    @staticmethod
    def is_vm_appliance(data):
        return data['device_type'] in ['dedicated_vm_appliance']

    @staticmethod
    def is_vcc(data):
        return 'is_vcc' in data and data['is_vcc'] is True

    @staticmethod
    def is_hypervisor(data):
        return data['device_type'] in ['hypervisor',
                                       'dedicated_hypervisor']

    @staticmethod
    def is_hypervisor_cluster(data):
        return data['device_type'] in ['hypervisor_cluster',
                                       'dedicated_hyp_clus']

    @staticmethod
    def is_matching(data1, data2, key):
        return data1[key] == data2[key]

    @staticmethod
    def is_dedicated(data):
        return 'dedicated' in data['device_type']

    @staticmethod
    def is_shared(data):
        return not BaseLogic.is_dedicated(data)

    @staticmethod
    def has_children(data):
        for k in ['hypervisors', 'hypervisor_clusters']:
            if k in data and len(data[k]):
                return True
        return False
