#!/usr/bin/env python
""" Base Validator """

import logging

from tornado import gen
from tornado.web import HTTPError

from app.logic.base import BaseLogic
from app.logic.vcenters import VCenterLogic
from app.logic.hypervisors import HypervisorLogic
from app.logic.hypervisor_clusters import HypervisorClusterLogic


log = logging.getLogger(__name__)


class BaseValidator(object):

    @staticmethod
    def is_vcc_validation(data):
        if not VCenterLogic.is_vcc(data):
            raise HTTPError(
                404,
                "No vCenter with ID: %s was found." % (
                    data['legacy_device_number']
                )
            )

    @staticmethod
    def is_existing_vcc_validation(data):
        if VCenterLogic.is_vcc(data):
            raise HTTPError(
                405,
                "Device %s is already a vcc." % (
                    data['legacy_device_number']
                )
            )

    @staticmethod
    def is_vm_validation(data):
        if not BaseLogic.is_vm(data):
            raise HTTPError(
                404,
                "No VM with ID: %s was found." % (
                    data['legacy_device_number']
                )
            )

    @staticmethod
    def is_vm_appliance_validation(data):
        if not BaseLogic.is_vm_appliance(data):
            raise HTTPError(
                404,
                "No VM with ID: %s was found." % (
                    data['legacy_device_number']
                )
            )

    @staticmethod
    def is_hypervisor_validation(data):
        if not HypervisorLogic.is_hypervisor(data):
            raise HTTPError(
                404,
                "No hypervisor with ID: %s was found." % (
                    data['legacy_device_number']
                )
            )

    @staticmethod
    def is_hypervisor_cluster_validation(data):
        if not HypervisorClusterLogic.is_hypervisor_cluster(data):
            raise HTTPError(
                404,
                "No hypervisor cluster with ID: %s was found." % (
                    data['legacy_device_number']
                )
            )

    @staticmethod
    def is_shared_validation(data):
        if not BaseLogic.is_shared(data):
            raise HTTPError(
                400,
                "Device {0} ({1}) is not of type \"shared\".".format(
                    data['legacy_device_number'],
                    data['name']
                )
            )

    @staticmethod
    def is_dedicated_validation(data):
        if not BaseLogic.is_dedicated(data):
            raise HTTPError(
                400,
                "Device {0} ({1}) is not of type \"dedicated\".".format(
                    data['legacy_device_number'],
                    data['name']
                )
            )

    @staticmethod
    def datacenter_validation(data1, data2):
        if not BaseLogic.is_matching(data1, data2, 'datacenter'):
            raise HTTPError(
                400,
                "Parent {0} ({1}) is not in the same "
                "datacenter as child {2} ({3}).".format(
                    data1['legacy_device_number'],
                    data1['name'],
                    data2['legacy_device_number'],
                    data2['name'])
            )

    @staticmethod
    def account_validation(data1, data2):
        if not BaseLogic.is_matching(data1, data2, 'customer_number'):
            raise HTTPError(
                400,
                "Parent {0} ({1}) does not have the same "
                "account as child {2} ({3}).".format(
                    data1['legacy_device_number'],
                    data1['name'],
                    data2['legacy_device_number'],
                    data2['name'])
            )

    @staticmethod
    @gen.engine
    def children_validation(data, callback):
        if BaseLogic.has_children(data):
            child = None
            if 'hypervisors' in data and data['hypervisors']:
                child = 'Hypervisors'
            if 'hypervisor_clusters' in data and data['hypervisor_clusters']:
                child = 'Hypervisor Clusters'
            raise HTTPError(
                400,
                "Device {0} ({1}) still has {2} associated to it".format(
                    data['legacy_device_number'],
                    data['name'],
                    child
                )
            )
        callback()
