from pysphere import VIServer, VITask, VIProperty
from pysphere.vi_virtual_machine import VIVirtualMachine
from pysphere.resources import VimService_services as VI


class Vsphere():
    def __init__(self, address, user, password, vm_path):
        self.server = VIServer()
        self.server.connect(address, user, password)
        self.vm = self.server.get_vm_by_path(vm_path)

    def __del__(self):
        if self.server:
            self.server.disconnect()

    def __change_cdrom_type(self, dev, dev_type, value=""):
        if dev_type == "ISO":
            iso = VI.ns0.VirtualCdromIsoBackingInfo_Def("iso").pyclass()
            iso.set_element_fileName(value)
            dev.set_element_backing(iso)
        elif dev_type == "HOST DEVICE":
            host = VI.ns0.VirtualCdromAtapiBackingInfo_Def("host").pyclass()
            host.set_element_deviceName(value)
            dev.set_element_backing(host)
        elif dev_type == "CLIENT DEVICE":
            client = VI.ns0.VirtualCdromRemoteAtapiBackingInfo_Def("client").pyclass()
            client.set_element_deviceName("")
            dev.set_element_backing(client)

    def __get_valid_host_devices(self, vm):
        env_browser = vm.properties.environmentBrowser._obj
        request = VI.QueryConfigTargetRequestMsg()
        _this = request.new__this(env_browser)
        _this.set_attribute_type(env_browser.get_attribute_type())
        request.set_element__this(_this)
        ret = self.server._proxy.QueryConfigTarget(request)._returnval
        return [cd.Name for cd in ret.CdRom]

    def __apply_changes(self, vm, cdrom):
        request = VI.ReconfigVM_TaskRequestMsg()
        _this = request.new__this(vm._mor)
        _this.set_attribute_type(vm._mor.get_attribute_type())
        request.set_element__this(_this)
        spec = request.new_spec()

        dev_change = spec.new_deviceChange()
        dev_change.set_element_device(cdrom)
        dev_change.set_element_operation("edit")

        spec.set_element_deviceChange([dev_change])
        request.set_element_spec(spec)
        ret = self.server._proxy.ReconfigVM_Task(request)._returnval

        task = VITask(ret, self.server)
        status = task.wait_for_state([task.STATE_SUCCESS,task.STATE_ERROR])
        if status == task.STATE_SUCCESS:
            result = True
        elif status == task.STATE_ERROR:
            result = False

        return result

    def mount_iso(self, iso):
        cdrom = None
        for dev in self.vm.properties.config.hardware.device:
            if dev._type == "VirtualCdrom":
                cdrom = dev._obj
                break

        self.__change_cdrom_type(cdrom, "ISO", iso)
        return self.__apply_changes(self.vm, cdrom)

    def unmount_iso(self):
        cdrom = None
        for dev in self.vm.properties.config.hardware.device:
            if dev._type == "VirtualCdrom":
                cdrom = dev._obj
                break

        self.__change_cdrom_type(cdrom, "CLIENT DEVICE")
        return self.__apply_changes(self.vm, cdrom)

    def get_iso_list(self, datastore, path="/", case_insensitive=True, folders_first=True, match_patterns=["*.iso"]):

        ds = [k for k,v in self.server.get_datastores().items() if v == datastore][0]
        ds_browser = VIProperty(self.server, ds).browser._obj

        request = VI.SearchDatastore_TaskRequestMsg()
        _this = request.new__this(ds_browser)
        _this.set_attribute_type(ds_browser.get_attribute_type())
        request.set_element__this(_this)
        request.set_element_datastorePath("[%s] %s" % (datastore, path))

        search_spec = request.new_searchSpec()

        query = [VI.ns0.FloppyImageFileQuery_Def('floppy').pyclass(),
                 VI.ns0.FolderFileQuery_Def('folder').pyclass(),
                 VI.ns0.IsoImageFileQuery_Def('iso').pyclass(),
                 VI.ns0.VmConfigFileQuery_Def('vm').pyclass(),
                 VI.ns0.TemplateConfigFileQuery_Def('template').pyclass(),
                 VI.ns0.VmDiskFileQuery_Def('vm_disk').pyclass(),
                 VI.ns0.VmLogFileQuery_Def('vm_log').pyclass(),
                 VI.ns0.VmNvramFileQuery_Def('vm_ram').pyclass(),
                 VI.ns0.VmSnapshotFileQuery_Def('vm_snapshot').pyclass()]
        search_spec.set_element_query(query)
        details = search_spec.new_details()
        details.set_element_fileOwner(True)
        details.set_element_fileSize(True)
        details.set_element_fileType(True)
        details.set_element_modification(True)
        search_spec.set_element_details(details)
        search_spec.set_element_searchCaseInsensitive(case_insensitive)
        search_spec.set_element_sortFoldersFirst(folders_first)
        search_spec.set_element_matchPattern(match_patterns)
        request.set_element_searchSpec(search_spec)
        response = self.server._proxy.SearchDatastore_Task(request)._returnval
        task = VITask(response, self.server)
        if task.wait_for_state([task.STATE_ERROR, task.STATE_SUCCESS]) == task.STATE_ERROR:
            raise Exception(task.get_error_message())

        info = task.get_result()

        iso_list = []
        if hasattr(info, "file"):
            for fi in info.file:
                iso_list.append(fi.path)
        
        return iso_list    

    def reboot(self, graceful=False):
        if graceful:
            task = self.vm.reboot_guest(sync_run=False)
        else:     
            task = self.vm.reset(sync_run=False)

        status = task.wait_for_state(['running', 'error'], timeout=10)    

        if status != "error":
            return True

    def shutdown(self, graceful=False):     
        if graceful:
            task = self.vm.shutdown_guest(sync_run=False)
        else:     
            task = self.vm.power_off(sync_run=False)

        status = task.wait_for_state(['running', 'error'], timeout=10)    

        if status != "error":
            return True

    def boot(self):
        task = self.vm.power_on(sync_run=False)        
        status = task.wait_for_state(['running', 'error'], timeout=10)    

        if status != "error":
            return True

    def get_statistics(self):
        statistics = self.vm.get_properties()   

        vhds = []
        for disk in statistics["disks"]:
            vhds.append({"label":disk["label"], "capacity":disk["capacity"]})

        iso = None
        for device in statistics["devices"]:
            if statistics["devices"][device]["type"] == "VirtualCdrom":
                iso = statistics["devices"][device]["summary"]  
                break
        if iso and iso != "Remote ATAPI":
            pos = iso.index(']')
            if pos:
                iso = iso[pos+2:]

        ip_address = self.vm.get_property('ip_address')

        state = self.vm.get_status(basic_status=False)

        stats = {
            "state": state,
            "vhds": vhds,
            "iso": iso,
            "vmwaretools_os": statistics["guest_full_name"],
            "vmwaretools_ip": ip_address,
            "memory": statistics["memory_mb"],
            "vcpus": statistics["num_cpu"],
            "name": statistics["name"],
        }

        return stats            

    def get_snapshots(self):
        snapshots = []
        for snapshot in self.vm.get_snapshots():
             snapshots.append({
                'name': snapshot.get_name(),
                'description': snapshot.get_description(),
                'create_time': snapshot.get_create_time(),
                'path': snapshot.get_path(),
                'state': snapshot.get_state(),
             })
        return snapshots

    def get_snapshots_count(self):
        return len(self.vm.get_snapshots())

    def delete_snapshot(self, path):
        try:
            self.vm.delete_snapshot_by_path(path, sync_run=True)              
            return True
        except:
            return False

    def revert_snapshot(self, path):
        task = self.vm.revert_to_path(path, sync_run=False)        
        status = task.wait_for_state(['running', 'error'], timeout=10)    

        if status != "error":
            return True             

    def create_snapshot(self, name, description):
        try:
            self.vm.create_snapshot(name, sync_run=True, description=description, memory=False, quiesce=False)      
            return True
        except:
            return False


#vsphere = Vsphere("bullsvsm.cybercon.net", "Administrator", "d@nc3fl00r", "[HeatNA1-BullsV08] Cybercon_Ben/Cybercon_Ben.vmx")
#print vsphere.get_iso_list("RocketsNA2-ISO")
#print vsphere.unmount_iso()

#print vsphere.mount_iso("[RocketsNA2-ISO] CentOS-5.6-i386-netinstall.iso")
#
#print get_iso_list("RocketsNA2-ISO")

