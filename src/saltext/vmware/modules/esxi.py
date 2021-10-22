# Copyright 2021 VMware, Inc.
# SPDX-License: Apache-2.0
import logging

import salt.exceptions
import saltext.vmware.utils.common as utils_common
import saltext.vmware.utils.esxi as utils_esxi
from saltext.vmware.utils.connect import get_service_instance

log = logging.getLogger(__name__)

try:
    from pyVmomi import vmodl, vim, VmomiSupport

    HAS_PYVMOMI = True
except ImportError:
    HAS_PYVMOMI = False


__virtualname__ = "vmware_esxi"


def __virtual__():
    if not HAS_PYVMOMI:
        return False, "Unable to import pyVmomi module."
    return __virtualname__


def get_lun_ids(service_instance=None):
    """
    Return a list of LUN (Logical Unit Number) NAA (Network Addressing Authority) IDs.
    """

    if service_instance is None:
        service_instance = get_service_instance(opts=__opts__, pillar=__pillar__)

    hosts = utils_esxi.get_hosts(service_instance=service_instance, get_all_hosts=True)
    ids = []
    for host in hosts:
        for datastore in host.datastore:
            for extent in datastore.info.vmfs.extent:
                ids.append(extent.diskName)
    return ids


def _get_capability_attribs(host):
    capability = host.capability
    ret = {
        "accel3d_supported": capability.accel3dSupported,
        "background_snapshots_supported": capability.backgroundSnapshotsSupported,
        "checkpoint_ft_compatibility_issues": list(capability.smpFtCompatibilityIssues),
        "checkpoint_ft_supported": capability.smpFtSupported,
        "clone_from_snapshot_supported": capability.cloneFromSnapshotSupported,
        "cpu_hw_mmu_supported": capability.cpuHwMmuSupported,
        "cpu_memory_resource_configuration_supported": capability.cpuMemoryResourceConfigurationSupported,
        "crypto_supported": capability.cryptoSupported,
        "datastore_principal_supported": capability.datastorePrincipalSupported,
        "delta_disk_backings_supported": capability.deltaDiskBackingsSupported,
        "eight_plus_host_vmfs_sharedAccess_supported": capability.eightPlusHostVmfsSharedAccessSupported,
        "encrypted_vmotion_supported": capability.encryptedVMotionSupported,
        "encryption_cbrc_supported": capability.encryptionCBRCSupported,
        "encryption_change_on_add_remove_supported": capability.encryptionChangeOnAddRemoveSupported,
        "encryption_fault_tolerance_supported": capability.encryptionFaultToleranceSupported,
        "encryption_hbr_supported": capability.encryptionHBRSupported,
        "encryption_hot_operation_supported": capability.encryptionHotOperationSupported,
        "encryption_memory_save_supported": capability.encryptionMemorySaveSupported,
        "encryption_rdm_supported": capability.encryptionRDMSupported,
        "encryption_vflash_supported": capability.encryptionVFlashSupported,
        "encryption_with_snapshots_supported": capability.encryptionWithSnapshotsSupported,
        "feature_capabilities_supported": capability.featureCapabilitiesSupported,
        "firewall_ip_rules_supported": capability.firewallIpRulesSupported,
        "ft_compatibility_issues": list(capability.ftCompatibilityIssues),
        "ft_supported": capability.ftSupported,
        "gateway_on_nic_supported": capability.gatewayOnNicSupported,
        "hbr_nic_selection_supported": capability.hbrNicSelectionSupported,
        "high_guest_mem_supported": capability.highGuestMemSupported,
        "host_access_manager_supported": capability.hostAccessManagerSupported,
        "inter_vm_communication_through_vmci_supported": capability.interVMCommunicationThroughVMCISupported,
        "ipmi_supported": capability.ipmiSupported,
        "iscsi_supported": capability.iscsiSupported,
        "latency_sensitivity_supported": capability.latencySensitivitySupported,
        "local_swap_datastore_supported": capability.localSwapDatastoreSupported,
        "login_by_ssl_thumbprint_supported": capability.loginBySSLThumbprintSupported,
        "maintenance_mode_supported": capability.maintenanceModeSupported,
        "mark_as_local_supported": capability.markAsLocalSupported,
        "mark_as_ssd_supported": capability.markAsSsdSupported,
        "max_host_running_vms": capability.maxHostRunningVms,
        "max_host_supported_vcpus": capability.maxHostSupportedVcpus,
        "max_num_disks_sv_motion": capability.maxNumDisksSVMotion,
        "max_registered_vms": capability.maxRegisteredVMs,
        "max_running_vms": capability.maxRunningVMs,
        "max_supported_vms": capability.maxSupportedVMs,
        "max_supported_vcpus": capability.maxSupportedVcpus,
        "max_vcpus_per_ft_vm": capability.maxVcpusPerFtVm,
        "message_bus_proxy_supported": capability.messageBusProxySupported,
        "multiple_network_stack_instance_supported": capability.multipleNetworkStackInstanceSupported,
        "nested_hv_supported": capability.nestedHVSupported,
        "nfs_41_krb5i_supported": capability.nfs41Krb5iSupported,
        "nfs_41_supported": capability.nfs41Supported,
        "nfs_supported": capability.nfsSupported,
        "nic_teaming_supported": capability.nicTeamingSupported,
        "one_k_volume_apis_supported": capability.oneKVolumeAPIsSupported,
        "per_vm_network_traffic_shaping_supported": capability.perVMNetworkTrafficShapingSupported,
        "per_vm_swap_files": capability.perVmSwapFiles,
        "pre_assigned_pci_unit_numbers_supported": capability.preAssignedPCIUnitNumbersSupported,
        "provisioning_nic_selection_supported": capability.provisioningNicSelectionSupported,
        "reboot_supported": capability.rebootSupported,
        "record_replay_supported": capability.recordReplaySupported,
        "recursive_resource_pools_supported": capability.recursiveResourcePoolsSupported,
        "reliable_memory_aware": capability.reliableMemoryAware,
        "replay_compatibility_issues": list(capability.replayCompatibilityIssues),
        "replay_unsupported_reason": capability.replayUnsupportedReason,
        "restricted_snapshot_relocate_supported": capability.restrictedSnapshotRelocateSupported,
        "san_supported": capability.sanSupported,
        "scaled_screenshot_supported": capability.scaledScreenshotSupported,
        "scheduled_hardware_upgrade_supported": capability.scheduledHardwareUpgradeSupported,
        "screenshot_supported": capability.screenshotSupported,
        "service_package_info_supported": capability.servicePackageInfoSupported,
        "shutdown_supported": capability.shutdownSupported,
        "smart_card_authentication_supported": capability.smartCardAuthenticationSupported,
        "smp_ft_compatibility_issues": list(capability.smpFtCompatibilityIssues),
        "smp_ft_supported": capability.smpFtSupported,
        "snapshot_relayout_supported": capability.snapshotRelayoutSupported,
        "standby_supported": capability.standbySupported,
        "storage_iorm_supported": capability.storageIORMSupported,
        "storage_policy_supported": capability.storagePolicySupported,
        "storage_vmotion_supported": capability.storageVMotionSupported,
        "supported_vmfs_major_version": list(capability.supportedVmfsMajorVersion),
        "suspended_relocate_supported": capability.suspendedRelocateSupported,
        "tpm_supported": capability.tpmSupported,
        "turn_disk_locator_led_supported": capability.turnDiskLocatorLedSupported,
        "unshared_swap_vmotion_supported": capability.unsharedSwapVMotionSupported,
        "upit_supported": capability.upitSupported,
        "vflash_supported": capability.vFlashSupported,
        "vpmc_supported": capability.vPMCSupported,
        "vstorage_capable": capability.vStorageCapable,
        "virtual_exec_usage_supported": capability.virtualExecUsageSupported,
        "virtual_volume_datastore_supported": capability.virtualVolumeDatastoreSupported,
        "vlan_tagging_supported": capability.vlanTaggingSupported,
        "vm_direct_path_gen_2_supported": capability.vmDirectPathGen2Supported,
        "vm_direct_path_gen_2_unsupported_reason": list(
            capability.vmDirectPathGen2UnsupportedReason
        ),
        "vm_direct_path_gen_2_unsupported_reason_extended": capability.vmDirectPathGen2UnsupportedReasonExtended,
        "vmfs_datastore_mount_capable": capability.vmfsDatastoreMountCapable,
        "vmotion_across_network_supported": capability.vmotionAcrossNetworkSupported,
        "vmotion_supported": capability.vmotionSupported,
        "vmotion_with_storage_vmotion_supported": capability.vmotionWithStorageVMotionSupported,
        "vr_nfc_nic_selection_supported": capability.vrNfcNicSelectionSupported,
        "vsan_supported": capability.vsanSupported,
    }
    return ret


def get_capabilities(service_instance=None):
    """
    Return ESXi host's capability information.
    """
    if service_instance is None:
        service_instance = get_service_instance(opts=__opts__, pillar=__pillar__)
    hosts = utils_esxi.get_hosts(service_instance=service_instance, get_all_hosts=True)
    capabilities = {}
    for host in hosts:
        capabilities[host.name] = _get_capability_attribs(host)
    return capabilities


def power_state(
    datacenter_name=None, cluster_name=None, host_name=None, state=None, timeout=600, force=True
):
    """
    Manage the power state of the ESXi host.

    datacenter_name
        Filter by this datacenter name (required when cluster is specified)

    cluster_name
        Filter by this cluster name (optional)

    host_name
        Filter by this ESXi hostname whose power state needs to be managed (optional).

    state
        Sets the ESXi host to this power state. Valid values: "reboot", "standby", "poweron", "shutdown".

    timeout
        Timeout when transitioning power state to standby / poweron. Default: 600 seconds

    force
        Force power state transition. Default: True


    .. code-block:: bash

        salt '*' vmware_esxi.power_state datacenter_name=dc1 cluster_name=cl1 host_name=host1 state=shutdown
    """
    ret = None
    task = None
    service_instance = get_service_instance(opts=__opts__, pillar=__pillar__)
    hosts = utils_esxi.get_hosts(
        service_instance=service_instance,
        host_names=[host_name] if host_name else None,
        cluster_name=cluster_name,
        datacenter_name=datacenter_name,
        get_all_hosts=host_name is None,
    )

    try:
        for h in hosts:
            if state == "reboot":
                task = h.RebootHost_Task(force)
            elif state == "standby":
                task = h.PowerDownHostToStandBy_Task(timeout, force)
            elif state == "poweron":
                task = h.PowerUpHostFromStandBy_Task(timeout)
            elif state == "shutdown":
                task = h.ShutdownHost_Task(force)
            if task:
                utils_common.wait_for_task(task, h.name, "PowerStateTask")
            ret = True
    except (vmodl.fault.NotSupported, salt.exceptions.VMwareApiError) as exc:
        raise salt.exceptions.SaltException(str(exc))
    return ret


def manage_service(
    service_name,
    datacenter_name=None,
    cluster_name=None,
    host_name=None,
    state=None,
    startup_policy=None,
    service_instance=None,
):
    """
    Manage the state of the service running on the EXSI host.

    service_name
        Service that needs to be managed.

    datacenter_name
        Filter by this datacenter name (required when cluster is specified)

    cluster_name
        Filter by this cluster name (optional)

    host_name
        Filter by this ESXi hostname whose power state needs to be managed (optional)

    state
        Sets the service running on the ESXi host to this state. Valid values: "start", "stop", "restart".

    startup_policy
        Sets the service startup policy. If unspecified, no changes are made. Valid values "on", "off", "automatic".
        - on: Start and stop with host
        - off: Start and stop manually
        - automatic: Start automatically if any ports are open, and stop when all ports are closed

    service_instance
        Use this vCenter service connection instance instead of creating a new one. (optional)

    .. code-block:: bash

        salt '*' vmware_esxi.manage_service sshd datacenter_name=dc1 cluster_name=cl1 host_name=host1 state=restart startup_policy=on
    """
    log.debug("Running vmware_esxi.manage_service")
    ret = None
    task = None
    if not service_instance:
        service_instance = get_service_instance(opts=__opts__, pillar=__pillar__)
    hosts = utils_esxi.get_hosts(
        service_instance=service_instance,
        host_names=[host_name] if host_name else None,
        cluster_name=cluster_name,
        datacenter_name=datacenter_name,
        get_all_hosts=host_name is None,
    )

    try:
        for h in hosts:
            host_service = h.configManager.serviceSystem
            if not host_service:
                continue
            if state:
                if state == "start":
                    host_service.StartService(id=service_name)
                elif state == "stop":
                    host_service.StopService(id=service_name)
                elif state == "restart":
                    host_service.RestartService(id=service_name)
                else:
                    raise salt.exceptions.SaltException("Unknown state - {}".format(state))
            if startup_policy is not None:
                if startup_policy is True:
                    startup_policy = "on"
                elif startup_policy is False:
                    startup_policy = "off"
                host_service.UpdateServicePolicy(id=service_name, policy=startup_policy)
        ret = True
    except (
        vim.fault.InvalidState,
        vim.fault.NotFound,
        vim.fault.HostConfigFault,
        vmodl.fault.InvalidArgument,
        salt.exceptions.VMwareApiError,
    ) as exc:
        raise salt.exceptions.SaltException(str(exc))
    return ret


def list_services(
    service_name=None,
    datacenter_name=None,
    cluster_name=None,
    host_name=None,
    state=None,
    startup_policy=None,
    service_instance=None,
):
    """
    List the state of services running on matching EXSI hosts.

    service_name
        Filter by this service name. (optional)

    datacenter_name
        Filter by this datacenter name (required when cluster is specified)

    cluster_name
        Filter by this cluster name (optional)

    host_name
        Filter by this ESXi hostname (optional)

    state
        Filter by this service state. Valid values: "running", "stopped"

    startup_policy
        Filter by this service startup policy. Valid values "on", "off", "automatic".

    service_instance
        Use this vCenter service connection instance instead of creating a new one. (optional).

    .. code-block:: bash

        salt '*' vmware_esxi.list_services
    """
    log.debug("Running vmware_esxi.list_services")
    ret = {}
    if not service_instance:
        service_instance = get_service_instance(opts=__opts__, pillar=__pillar__)
    hosts = utils_esxi.get_hosts(
        service_instance=service_instance,
        host_names=[host_name] if host_name else None,
        cluster_name=cluster_name,
        datacenter_name=datacenter_name,
        get_all_hosts=host_name is None,
    )

    try:
        for h in hosts:
            host_service = h.configManager.serviceSystem
            ret[h.name] = {}
            if not host_service:
                continue
            if startup_policy is not None:
                # salt converts command line input "on" and "off" to True and False. Handle explicitly.
                if startup_policy is True:
                    startup_policy = "on"
                elif startup_policy is False:
                    startup_policy = "off"
            services = host_service.serviceInfo.service
            for service in services or []:
                if service_name and service.key != service_name:
                    continue
                if startup_policy and service.policy != startup_policy:
                    continue
                if state and state == "running" and not service.running:
                    continue
                if state and state == "stopped" and service.running:
                    continue
                ret[h.name][service.key] = {
                    "state": "running" if service.running else "stopped",
                    "startup_policy": service.policy,
                }
    except (
        vim.fault.InvalidState,
        vim.fault.NotFound,
        vim.fault.HostConfigFault,
        vmodl.fault.InvalidArgument,
        salt.exceptions.VMwareApiError,
    ) as exc:
        raise salt.exceptions.SaltException(str(exc))
    return ret


def get_acceptance_level(
    datacenter_name=None,
    cluster_name=None,
    host_name=None,
    acceptance_level=None,
    service_instance=None,
):
    """
    Get acceptance level on matching EXSI hosts.

    datacenter_name
        Filter by this datacenter name (required when cluster is specified)

    cluster_name
        Filter by this cluster name (optional)

    host_name
        Filter by this ESXi hostname (optional)

    acceptance_level
        Filter by this acceptance level. Valid values: "community", "partner", "vmware_accepted", "vmware_certified". (optional)

    service_instance
        Use this vCenter service connection instance instead of creating a new one. (optional).

    .. code-block:: bash

        salt '*' vmware_esxi.get_acceptance_level

    Returns:

    .. code-block:: json

        {
            "host1": "partner",
            "host2": "partner"
        }

    """

    log.debug("Running vmware_esxi.get_acceptance_level")
    ret = {}
    if not service_instance:
        service_instance = get_service_instance(opts=__opts__, pillar=__pillar__)
    hosts = utils_esxi.get_hosts(
        service_instance=service_instance,
        host_names=[host_name] if host_name else None,
        cluster_name=cluster_name,
        datacenter_name=datacenter_name,
        get_all_hosts=host_name is None,
    )

    try:
        for h in hosts:
            host_config_manager = h.configManager.imageConfigManager
            if not host_config_manager:
                continue
            host_acceptance_level = host_config_manager.HostImageConfigGetAcceptance()
            if acceptance_level and host_acceptance_level != acceptance_level:
                continue
            ret[h.name] = host_acceptance_level
    except (
        vim.fault.InvalidState,
        vim.fault.NotFound,
        vim.fault.HostConfigFault,
        vmodl.fault.InvalidArgument,
        salt.exceptions.VMwareApiError,
    ) as exc:
        raise salt.exceptions.SaltException(str(exc))
    return ret


def set_acceptance_level(
    acceptance_level,
    datacenter_name=None,
    cluster_name=None,
    host_name=None,
    service_instance=None,
):
    """
    Set acceptance level on matching EXSI hosts.

    acceptance_level
        Set to this acceptance level. Valid values: "community", "partner", "vmware_accepted", "vmware_certified".

    datacenter_name
        Filter by this datacenter name (required when cluster is specified)

    cluster_name
        Filter by this cluster name (optional)

    host_name
        Filter by this ESXi hostname (optional)

    service_instance
        Use this vCenter service connection instance instead of creating a new one. (optional).

    .. code-block:: bash

        salt '*' vmware_esxi.set_acceptance_level

    Returns:

    .. code-block:: json

        {
            "host1": "partner",
            "host2": "partner"
        }

    """

    log.debug("Running vmware_esxi.set_acceptance_level")
    ret = {}
    if not service_instance:
        service_instance = get_service_instance(opts=__opts__, pillar=__pillar__)
    hosts = utils_esxi.get_hosts(
        service_instance=service_instance,
        host_names=[host_name] if host_name else None,
        cluster_name=cluster_name,
        datacenter_name=datacenter_name,
        get_all_hosts=host_name is None,
    )

    try:
        for h in hosts:
            host_config_manager = h.configManager.imageConfigManager
            if not host_config_manager:
                continue
            host_config_manager.UpdateHostImageAcceptanceLevel(newAcceptanceLevel=acceptance_level)
            ret[h.name] = acceptance_level
    except (
        vim.fault.InvalidState,
        vim.fault.NotFound,
        vim.fault.HostConfigFault,
        vmodl.fault.InvalidArgument,
        salt.exceptions.VMwareApiError,
    ) as exc:
        raise salt.exceptions.SaltException(str(exc))
    return ret


def get_advanced_config(
    datacenter_name=None,
    cluster_name=None,
    host_name=None,
    config_name=None,
    service_instance=None,
):
    """
    Get advanced config on matching EXSI hosts.

    datacenter_name
        Filter by this datacenter name (required when cluster is specified)

    cluster_name
        Filter by this cluster name (optional)

    host_name
        Filter by this ESXi hostname (optional)

    config_name
        Filter by this config_name. (optional)

    service_instance
        Use this vCenter service connection instance instead of creating a new one. (optional).

    .. code-block:: bash

        salt '*' vmware_esxi.get_advanced_config
    """
    log.debug("Running vmware_esxi.get_advanced_config")
    ret = {}
    if not service_instance:
        service_instance = get_service_instance(opts=__opts__, pillar=__pillar__)
    hosts = utils_esxi.get_hosts(
        service_instance=service_instance,
        host_names=[host_name] if host_name else None,
        cluster_name=cluster_name,
        datacenter_name=datacenter_name,
        get_all_hosts=host_name is None,
    )

    try:
        for h in hosts:
            config_manager = h.configManager.advancedOption
            ret[h.name] = {}
            if not config_manager:
                continue
            for opt in config_manager.QueryOptions(config_name):
                ret[h.name][opt.key] = opt.value

    except (
        vim.fault.InvalidState,
        vim.fault.NotFound,
        vim.fault.HostConfigFault,
        vmodl.fault.InvalidArgument,
        salt.exceptions.VMwareApiError,
    ) as exc:
        raise salt.exceptions.SaltException(str(exc))
    return ret


def set_advanced_configs(
    config_dict,
    datacenter_name=None,
    cluster_name=None,
    host_name=None,
    service_instance=None,
):
    """
    Set multiple advanced configurations on matching EXSI hosts.

    config_dict
        Set the configuration key to the configuration value. Eg: {"Annotations.WelcomeMessage": "Hello"}

    datacenter_name
        Filter by this datacenter name (required when cluster is specified)

    cluster_name
        Filter by this cluster name (optional)

    host_name
        Filter by this ESXi hostname (optional)

    service_instance
        Use this vCenter service connection instance instead of creating a new one. (optional).

    .. code-block:: bash

        salt '*' vmware_esxi.set_advanced_config config_name=Annotations.WelcomeMessage config_value=Hello

    Returns:

    .. code-block:: json

        {
            "host1": {
                "Annotations.WelcomeMessage": "HelloDemo"
            },
        }

    """
    log.debug("Running vmware_esxi.set_advanced_configs")
    ret = {}
    if not service_instance:
        service_instance = get_service_instance(opts=__opts__, pillar=__pillar__)
    hosts = utils_esxi.get_hosts(
        service_instance=service_instance,
        host_names=[host_name] if host_name else None,
        cluster_name=cluster_name,
        datacenter_name=datacenter_name,
        get_all_hosts=host_name is None,
    )

    try:
        for h in hosts:
            config_manager = h.configManager.advancedOption
            ret[h.name] = {}
            if not config_manager:
                continue

            supported_configs = {}
            for opt in config_manager.supportedOption:
                if opt.key not in config_dict:
                    continue
                supported_configs[opt.key] = opt.optionType

            advanced_configs = []
            for opt in config_dict:
                opt_type = supported_configs[opt]
                val = config_dict[opt]
                if isinstance(opt_type, vim.option.BoolOption) and not isinstance(val, bool):
                    val = val.lower() == "true"
                elif isinstance(opt_type, vim.option.LongOption):
                    val = VmomiSupport.vmodlTypes["long"](val)
                elif isinstance(opt_type, vim.option.IntOption):
                    val = VmomiSupport.vmodlTypes["int"](val)
                advanced_configs.append(vim.option.OptionValue(key=opt, value=val))
                ret[h.name][opt] = config_dict[opt]
            config_manager.UpdateOptions(changedValue=advanced_configs)
    except (
        vim.fault.InvalidState,
        vim.fault.NotFound,
        vim.fault.HostConfigFault,
        vmodl.fault.InvalidArgument,
        salt.exceptions.VMwareApiError,
    ) as exc:
        raise salt.exceptions.SaltException(str(exc))
    return ret


def set_advanced_config(
    config_name,
    config_value,
    datacenter_name=None,
    cluster_name=None,
    host_name=None,
    service_instance=None,
):
    """
    Set a single advanced configuration on matching EXSI hosts.

    config_name
        Name of the advanced configuration to be set.

    config_value
        Set the advanced configuration to this value.

    datacenter_name
        Filter by this datacenter name (required when cluster is specified)

    cluster_name
        Filter by this cluster name (optional)

    host_name
        Filter by this ESXi hostname (optional)

    service_instance
        Use this vCenter service connection instance instead of creating a new one. (optional).

    .. code-block:: bash

        salt '*' vmware_esxi.set_advanced_config config_name=Annotations.WelcomeMessage config_value=Hello

    Returns:

    .. code-block:: json

        {
            "host1": {
                "Annotations.WelcomeMessage": "HelloDemo"
            },
        }

    """
    log.debug("Running vmware_esxi.set_advanced_config")
    return set_advanced_configs(
        config_dict={config_name: config_value},
        datacenter_name=datacenter_name,
        cluster_name=cluster_name,
        host_name=host_name,
        service_instance=service_instance,
    )


def get_dns_config(
    datacenter_name=None,
    cluster_name=None,
    host_name=None,
    service_instance=None,
):
    """
    Get DNS configuration on matching EXSI hosts.

    datacenter_name
        Filter by this datacenter name (required when cluster is specified)

    cluster_name
        Filter by this cluster name (optional)

    host_name
        Filter by this ESXi hostname (optional)

    service_instance
        Use this vCenter service connection instance instead of creating a new one. (optional).

    .. code-block:: bash

        salt '*' vmware_esxi.get_dns_config
    """
    log.debug("Running vmware_esxi.get_dns_config")
    ret = {}
    if not service_instance:
        service_instance = get_service_instance(opts=__opts__, pillar=__pillar__)
    hosts = utils_esxi.get_hosts(
        service_instance=service_instance,
        host_names=[host_name] if host_name else None,
        cluster_name=cluster_name,
        datacenter_name=datacenter_name,
        get_all_hosts=host_name is None,
    )

    try:
        for h in hosts:
            dns_config = h.config.network.dnsConfig
            if not dns_config:
                continue
            ret[h.name] = {}
            ret[h.name]["dhcp"] = dns_config.dhcp
            ret[h.name]["virtual_nic"] = dns_config.virtualNicDevice
            ret[h.name]["host_name"] = dns_config.hostName
            ret[h.name]["domain_name"] = dns_config.domainName
            ret[h.name]["ip"] = list(dns_config.address)
    except (
        vim.fault.InvalidState,
        vim.fault.NotFound,
        vim.fault.HostConfigFault,
        vmodl.fault.InvalidArgument,
        salt.exceptions.VMwareApiError,
    ) as exc:
        raise salt.exceptions.SaltException(str(exc))
    return ret


def connect(host, service_instance=None):
    """
    Connect an ESXi instance to a vCenter instance.

    host
        Name of ESXi instance in vCenter.

    service_instance
        The Service Instance from which to obtain managed object references. (Optional)
    """
    log.debug(f"Connect ESXi instance {host}.")
    if service_instance is None:
        service_instance = get_service_instance(opts=__opts__, pillar=__pillar__)

    state = utils_esxi.reconnect_host(host, service_instance)
    return {"state": state}


def disconnect(host, service_instance=None):
    """
    Disconnect an ESXi instance.

    host
        Name of ESXi instance in vCenter.

    service_instance
        The Service Instance from which to obtain managed object references. (Optional)
    """
    log.debug(f"Disconnect ESXi instance {host}.")
    if service_instance is None:
        service_instance = get_service_instance(opts=__opts__, pillar=__pillar__)

    state = utils_esxi.disconnect_host(host, service_instance)
    return {"state": state}


def remove(host, service_instance=None):
    """
    Remove an ESXi instance from a vCenter instance.

    host
        Name of ESXi instance in vCenter.

    service_instance
        The Service Instance from which to obtain managed object references. (Optional)
    """
    log.debug(f"Remove ESXi instance {host}.")
    if service_instance is None:
        service_instance = get_service_instance(opts=__opts__, pillar=__pillar__)

    state = utils_esxi.remove_host(host, service_instance)
    return {"state": state}


def move(host, cluster_name, service_instance=None):
    """
    Move an ESXi instance to a different cluster.

    host
        Name of ESXi instance in vCenter.

    cluster_name
        Name of cluster to move host to.

    service_instance
        The Service Instance from which to obtain managed object references. (Optional)
    """
    log.debug(f"Move ESXi instance {host}.")
    if service_instance is None:
        service_instance = get_service_instance(opts=__opts__, pillar=__pillar__)

    state = utils_esxi.move_host(host, cluster_name, service_instance)
    return {"state": state}


def add(
    host,
    root_user,
    password,
    cluster_name,
    datacenter_name,
    verify_host_cert=True,
    connect=True,
    service_instance=None,
):
    """
    Add an ESXi instance to a vCenter instance.

    host
        IP address or hostname of ESXi instance.

    root_user
        Username with root privilege to ESXi instance.

    password
        Password to root user.

    cluster_name
        Name of cluster ESXi host is being added to.

    datacenter
        Datacenter that contains cluster that ESXi instance is being added to.

    verify_host_cert
        Validates the host's SSL certificate is signed by a CA, and that the hostname in the certificate matches the host. Defaults to True.

    connect
        Specifies whether host should be connected after being added. Defaults to True.

    service_instance
        The Service Instance from which to obtain managed object references. (Optional)
    """
    log.debug(f"Adding ESXi instance {host}.")
    if service_instance is None:
        service_instance = get_service_instance(opts=__opts__, pillar=__pillar__)
    state = utils_esxi.add_host(
        host,
        root_user,
        password,
        cluster_name,
        datacenter_name,
        verify_host_cert,
        connect,
        service_instance,
    )
    return {"state": state}


def list_pkgs(
    pkg_name=None,
    datacenter_name=None,
    cluster_name=None,
    host_name=None,
    service_instance=None,
):
    """
    List the packages installed on matching EXSi hosts.
    Note: Appropriate filters are recommended for large installations.

    pkg_name
        Filter by this package name. (optional)

    datacenter_name
        Filter by this datacenter name (required when cluster is specified)

    cluster_name
        Filter by this cluster name (optional)

    host_name
        Filter by this ESXi hostname (optional)

    service_instance
        Use this vCenter service connection instance instead of creating a new one. (optional).

    .. code-block:: bash

        salt '*' vmware_esxi.list_pkgs
    """
    log.debug("Running vmware_esxi.list_pkgs")
    ret = {}
    if not service_instance:
        service_instance = get_service_instance(opts=__opts__, pillar=__pillar__)
    hosts = utils_esxi.get_hosts(
        service_instance=service_instance,
        host_names=[host_name] if host_name else None,
        cluster_name=cluster_name,
        datacenter_name=datacenter_name,
        get_all_hosts=host_name is None,
    )

    try:
        for h in hosts:
            host_pkg_manager = h.configManager.imageConfigManager
            if not host_pkg_manager:
                continue
            ret[h.name] = {}
            pkgs = host_pkg_manager.FetchSoftwarePackages()
            for pkg in pkgs:
                if pkg_name and pkg.name != pkg_name:
                    continue
                ret[h.name][pkg.name] = {
                    "version": pkg.version,
                    "vendor": pkg.vendor,
                    "summary": pkg.summary,
                    "description": pkg.description,
                    "acceptance_level": pkg.acceptanceLevel,
                    "maintenance_mode_required": pkg.maintenanceModeRequired,
                    "creation_date": pkg.creationDate,
                }
        return ret
    except (
        vim.fault.InvalidState,
        vim.fault.NotFound,
        vim.fault.HostConfigFault,
        vmodl.fault.InvalidArgument,
        salt.exceptions.VMwareApiError,
    ) as exc:
        raise salt.exceptions.SaltException(str(exc))


def get(
    datacenter_name=None,
    cluster_name=None,
    host_name=None,
    service_instance=None,
):
    """
    Get configuration information for matching EXSI hosts.

    datacenter_name
        Filter by this datacenter name (required when cluster is specified)

    cluster_name
        Filter by this cluster name (optional)

    host_name
        Filter by this ESXi hostname (optional)

    service_instance
        Use this vCenter service connection instance instead of creating a new one. (optional).

    .. code-block:: bash

        salt '*' vmware_esxi.get dc1 cl1
    """
    log.debug("Running vmware_esxi.get")
    ret = {}
    if not service_instance:
        service_instance = get_service_instance(opts=__opts__, pillar=__pillar__)
    hosts = utils_esxi.get_hosts(
        service_instance=service_instance,
        host_names=[host_name] if host_name else None,
        cluster_name=cluster_name,
        datacenter_name=datacenter_name,
        get_all_hosts=host_name is None,
    )

    try:
        for h in hosts:
            ret[h.name] = {}
            vsan_manager = h.configManager.vsanSystem
            if vsan_manager:
                vsan = vsan_manager.QueryHostStatus()
                ret[h.name]["vsan_cluster_uuid"] = vsan.uuid
                ret[h.name]["vsan_node_uuid"] = vsan.nodeUuid
                ret[h.name]["vsan_health"] = vsan.health

            ret[h.name]["cpu_model"] = h.summary.hardware.cpuModel
            ret[h.name]["num_cpu_cores"] = h.summary.hardware.numCpuCores
            ret[h.name]["num_cpu_pkgs"] = h.summary.hardware.numCpuPkgs
            ret[h.name]["num_cpu_threads"] = h.summary.hardware.numCpuThreads
            ret[h.name]["memory_size"] = h.summary.hardware.memorySize
            ret[h.name]["overall_memory_usage"] = h.summary.quickStats.overallMemoryUsage

            for store in h.datastore:
                ret[h.name][store.name] = {}
                ret[h.name][store.name]["capacity"] = store.summary.capacity
                ret[h.name][store.name]["free_space"] = store.summary.freeSpace

            ret[h.name]["nics"] = {}
            for nic in h.config.network.vnic:
                ret[h.name]["nics"][nic.device] = {}
                ret[h.name]["nics"][nic.device]["ip_address"] = nic.spec.ip.ipAddress
                ret[h.name]["nics"][nic.device]["subnet_mask"] = nic.spec.ip.subnetMask
                ret[h.name]["nics"][nic.device]["mac"] = nic.spec.mac
                ret[h.name]["nics"][nic.device]["mtu"] = nic.spec.mtu

            ret[h.name]["product_name"] = h.config.product.name
            ret[h.name]["product_version"] = h.config.product.version
            ret[h.name]["product_build"] = h.config.product.build
            ret[h.name]["product_os_type"] = h.config.product.osType
            ret[h.name]["host_name"] = h.summary.config.name
            ret[h.name]["system_vendor"] = h.hardware.systemInfo.vendor
            ret[h.name]["system_model"] = h.hardware.systemInfo.model
            ret[h.name]["bois_release_date"] = h.hardware.biosInfo.releaseDate
            ret[h.name]["bois_release_version"] = h.hardware.biosInfo.biosVersion
            ret[h.name]["uptime"] = h.summary.quickStats.uptime
            ret[h.name]["in_maintenance_mode"] = h.runtime.inMaintenanceMode
            ret[h.name]["system_uuid"] = h.hardware.systemInfo.uuid
            for info in h.hardware.systemInfo.otherIdentifyingInfo:
                ret[h.name].setdefault("other_info", {}).update(
                    {info.identifierType.key: info.identifierValue}
                )
            ret[h.name]["capabilities"] = _get_capability_attribs(host=h)
        return ret
    except (
        vim.fault.InvalidState,
        vim.fault.NotFound,
        vim.fault.HostConfigFault,
        vmodl.fault.InvalidArgument,
        salt.exceptions.VMwareApiError,
    ) as exc:
        raise salt.exceptions.SaltException(str(exc))
