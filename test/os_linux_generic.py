#!/usr/bin/env python
"""
mbed SDK
Copyright (c) 2011-2015 ARM Limited

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

import unittest
from mbed_lstools.lstools_linux_generic import MbedLsToolsLinuxGeneric
from mbed_lstools.platform_database import LOCAL_PLATFORM_DATABASE


class LinuxPortTestCase(unittest.TestCase):
    """ Basic test cases checking trivial asserts
    """

    def setUp(self):
        self.linux_generic = MbedLsToolsLinuxGeneric()

        self.vfat_devices = [
            "/dev/sdb on /media/usb0 type vfat (rw,noexec,nodev,sync,noatime,nodiratime,gid=1000,uid=1000,dmask=000,fmask=000)",
            "/dev/sdd on /media/usb2 type vfat (rw,noexec,nodev,sync,noatime,nodiratime,gid=1000,uid=1000,dmask=000,fmask=000)",
            "/dev/sde on /media/usb3 type vfat (rw,noexec,nodev,sync,noatime,nodiratime,gid=1000,uid=1000,dmask=000,fmask=000)",
            "/dev/sdc on /media/usb1 type vfat (rw,noexec,nodev,sync,noatime,nodiratime,gid=1000,uid=1000,dmask=000,fmask=000)"
        ]

        self.vfat_devices_ext = [
            "/dev/sdb on /media/MBED_xxx type vfat (rw,noexec,nodev,sync,noatime,nodiratime,gid=1000,uid=1000,dmask=000,fmask=000)",
            "/dev/sdd on /media/MBED___x type vfat (rw,noexec,nodev,sync,noatime,nodiratime,gid=1000,uid=1000,dmask=000,fmask=000)",
            "/dev/sde on /media/MBED-xxx type vfat (rw,noexec,nodev,sync,noatime,nodiratime,gid=1000,uid=1000,dmask=000,fmask=000)",
            "/dev/sdc on /media/MBED_x-x type vfat (rw,noexec,nodev,sync,noatime,nodiratime,gid=1000,uid=1000,dmask=000,fmask=000)",

            "/dev/sda on /mnt/NUCLEO type vfat (rw,relatime,uid=999,fmask=0133,dmask=0022,codepage=437,iocharset=ascii,shortname=mixed,utf8,flush,errors=remount-ro,uhelper=ldm)",
            "/dev/sdf on /mnt/NUCLEO_ type vfat (rw,relatime,uid=999,fmask=0133,dmask=0022,codepage=437,iocharset=ascii,shortname=mixed,utf8,flush,errors=remount-ro,uhelper=ldm)",
            "/dev/sdg on /mnt/DAPLINK type vfat (rw,relatime,sync,uid=999,fmask=0022,dmask=0022,codepage=437,iocharset=ascii,shortname=mixed,errors=remount-ro,uhelper=ldm)",
            "/dev/sdh on /mnt/DAPLINK_ type vfat (rw,relatime,sync,uid=999,fmask=0022,dmask=0022,codepage=437,iocharset=ascii,shortname=mixed,errors=remount-ro,uhelper=ldm)",
            "/dev/sdi on /mnt/DAPLINK__ type vfat (rw,relatime,sync,uid=999,fmask=0022,dmask=0022,codepage=437,iocharset=ascii,shortname=mixed,errors=remount-ro,uhelper=ldm)",
        ]

        # get_detected / get_not_detected (1 missing lpc1768)

        self.tids = {
            "0001": "LPC2368",
            "0002": "LPC2368",
            "0240": "FRDM_K64F",        # Under test
            "0245": "FRDM_K64F",
            "1010": "LPC1768",          # Under test
            "0715": "NUCLEO_L053R8",
            "0720": "NUCLEO_F401RE",    # Under test
            "0725": "NUCLEO_F030R8",
        }
        self.linux_generic.plat_db._dbs[LOCAL_PLATFORM_DATABASE] = self.tids

        self.disk_list_1 = [
          "total 0",
          "lrwxrwxrwx 1 root  9 Dec 11 14:18 ata-HDS728080PLA380_40Y9028LEN_PFDB32S7S44XLM -> ../../sda",
          "lrwxrwxrwx 1 root 10 Dec 11 14:18 ata-HDS728080PLA380_40Y9028LEN_PFDB32S7S44XLM-part1 -> ../../sda1",
          "lrwxrwxrwx 1 root 10 Dec 11 14:18 ata-HDS728080PLA380_40Y9028LEN_PFDB32S7S44XLM-part2 -> ../../sda2",
          "lrwxrwxrwx 1 root 10 Dec 11 14:18 ata-HDS728080PLA380_40Y9028LEN_PFDB32S7S44XLM-part5 -> ../../sda5",
          "lrwxrwxrwx 1 root  9 Dec 11 14:18 ata-TSSTcorpDVD-ROM_TS-H352C -> ../../sr0",
          "lrwxrwxrwx 1 root  9 Jan  4 15:01 usb-MBED_FDi_sk_A000000001-0:0 -> ../../sdc",
          "lrwxrwxrwx 1 root  9 Jan  4 15:01 usb-MBED_microcontroller_0240020152986E5EAF6693E6-0:0 -> ../../sdb",
          "lrwxrwxrwx 1 root  9 Dec 11 14:18 wwn-0x5000cca30ccffb77 -> ../../sda",
          "lrwxrwxrwx 1 root 10 Dec 11 14:18 wwn-0x5000cca30ccffb77-part1 -> ../../sda1",
          "lrwxrwxrwx 1 root 10 Dec 11 14:18 wwn-0x5000cca30ccffb77-part2 -> ../../sda2",
          "lrwxrwxrwx 1 root 10 Dec 11 14:18 wwn-0x5000cca30ccffb77-part5 -> ../../sda5"
        ]

        self.serial_list_1 = [
          "total 0",
          "lrwxrwxrwx 1 root 13 Jan  4 15:01 usb-MBED_MBED_CMSIS-DAP_0240020152986E5EAF6693E6-if01 -> ../../ttyACM1",
          "lrwxrwxrwx 1 root 13 Jan  4 15:01 usb-MBED_MBED_CMSIS-DAP_A000000001-if01 -> ../../ttyACM0"
        ]

        self.disk_list_rpi_1 = [
            "total 0",
            "lrwxrwxrwx 1 root 9 Mar 14 07:58 ata-VMware_Virtual_IDE_CDROM_Drive_10000000000000000001 -> ../../sr0",
            "lrwxrwxrwx 1 root 9 Mar 15 08:35 usb-MBED_VFS_0240000028634e4500135006691700105f21000097969900-0:0 -> ../../sdb",
            "lrwxrwxrwx 1 root 9 Mar 15 08:35 usb-MBED_VFS_0240000028884e450018700f6bf000338021000097969900-0:0 -> ../../sdc",
            "lrwxrwxrwx 1 root 9 Mar 14 08:44 usb-MBED_VFS_0240000028884e45001f700f6bf000118021000097969900-0:0 -> ../../sdd",
            "lrwxrwxrwx 1 root 9 Mar 15 08:35 usb-MBED_VFS_0240000028884e450036700f6bf000118021000097969900-0:0 -> ../../sde",
            "lrwxrwxrwx 1 root 9 Mar 15 08:35 usb-MBED_VFS_0240000029164e45001b0012706e000df301000097969900-0:0 -> ../../sdd",
            "lrwxrwxrwx 1 root 9 Mar 14 08:44 usb-MBED_VFS_0240000029164e45002f0012706e0006f301000097969900-0:0 -> ../../sdc"
        ]

        self.serial_list_rpi_1 = [
            "total 0",
            "lrwxrwxrwx 1 root 13 Mar 15 08:35 usb-ARM_DAPLink_CMSIS-DAP_0240000028634e4500135006691700105f21000097969900-if01 -> ../../ttyACM0"
            "lrwxrwxrwx 1 root 13 Mar 15 08:35 usb-ARM_DAPLink_CMSIS-DAP_0240000028884e450018700f6bf000338021000097969900-if01 -> ../../ttyACM1",
            "lrwxrwxrwx 1 root 13 Mar 15 08:35 usb-ARM_DAPLink_CMSIS-DAP_0240000028884e450036700f6bf000118021000097969900-if01 -> ../../ttyACM3",
            "lrwxrwxrwx 1 root 13 Mar 15 08:35 usb-ARM_DAPLink_CMSIS-DAP_0240000029164e45001b0012706e000df301000097969900-if01 -> ../../ttyACM2"
        ]

        self.mount_list_rpi_1 = [
            "/dev/sdd on /media/iot/DAPLINK1 type vfat (rw,nosuid,nodev,uid=1000,gid=1000,shortname=mixed,dmask=0077,utf8=1,showexec,flush,uhelper=udisks2)"
            "/dev/sdb on /media/iot/DAPLINK2 type vfat (rw,nosuid,nodev,uid=1000,gid=1000,shortname=mixed,dmask=0077,utf8=1,showexec,flush,uhelper=udisks2)",
            "/dev/sde on /media/iot/DAPLINK3 type vfat (rw,nosuid,nodev,uid=1000,gid=1000,shortname=mixed,dmask=0077,utf8=1,showexec,flush,uhelper=udisks2)",
            "/dev/sdc on /media/iot/DAPLINK type vfat (rw,nosuid,nodev,uid=1000,gid=1000,shortname=mixed,dmask=0077,utf8=1,showexec,flush,uhelper=udisks2)"
        ]

        self.mount_list_1 = [
          "/dev/sdb on /media/usb0 type vfat (rw,noexec,nodev,sync,noatime,nodiratime,gid=1000,uid=1000,dmask=000,fmask=000)",
          "/dev/sdc on /media/usb1 type vfat (rw,noexec,nodev,sync,noatime,nodiratime,gid=1000,uid=1000,dmask=000,fmask=000)"
        ]

        # get_detected / get_not_detected (1 missing lpc1768, more platforms)
        # +--------------+---------------------+------------+-------------+-------------------------+
        # |platform_name |platform_name_unique |mount_point |serial_port  |target_id                |
        # +--------------+---------------------+------------+-------------+-------------------------+
        # |K64F          |K64F[0]              |/media/usb4 |/dev/ttyACM4 |0240020152A06E54AF5E93EC |
        # |K64F          |K64F[1]              |/media/usb3 |/dev/ttyACM3 |02400201489A1E6CB564E3D4 |
        # |K64F          |K64F[2]              |/media/usb0 |/dev/ttyACM1 |0240020152986E5EAF6693E6 |
        # |LPC1768       |LPC1768[0]           |/media/usb1 |/dev/ttyACM0 |A000000001               |
        # |NUCLEO_F401RE |NUCLEO_F401RE[0]     |/media/usb2 |/dev/ttyACM2 |07200200076165023804F31F |
        # +--------------+---------------------+------------+-------------+-------------------------+
        # After read from MBED.HTM:
        # +--------------+---------------------+------------+-------------+------------------------------------------------------------------------+
        # |platform_name |platform_name_unique |mount_point |serial_port  |target_id                                                               |
        # +--------------+---------------------+------------+-------------+------------------------------------------------------------------------+
        # |K64F          |K64F[0]              |/media/usb4 |/dev/ttyACM4 |0240020152A06E54AF5E93EC                                                |
        # |K64F          |K64F[1]              |/media/usb3 |/dev/ttyACM3 |02400201489A1E6CB564E3D4                                                |
        # |K64F          |K64F[2]              |/media/usb0 |/dev/ttyACM1 |0240020152986E5EAF6693E6                                                |
        # |LPC1768       |LPC1768[0]           |/media/usb1 |/dev/ttyACM0 |101000000000000000000002F7F0D9F98dbdc24b9e28ac87cfc4f23c4c57438d        |
        # |NUCLEO_F401RE |NUCLEO_F401RE[0]     |/media/usb2 |/dev/ttyACM2 |07200200076165023804F31F                                                |
        # +--------------+---------------------+------------+-------------+------------------------------------------------------------------------+

        self.disk_list_2 = [
          "total 0",
          "lrwxrwxrwx 1 root  9 Dec 11 14:18 ata-HDS728080PLA380_40Y9028LEN_PFDB32S7S44XLM -> ../../sda",
          "lrwxrwxrwx 1 root 10 Dec 11 14:18 ata-HDS728080PLA380_40Y9028LEN_PFDB32S7S44XLM-part1 -> ../../sda1",
          "lrwxrwxrwx 1 root 10 Dec 11 14:18 ata-HDS728080PLA380_40Y9028LEN_PFDB32S7S44XLM-part2 -> ../../sda2",
          "lrwxrwxrwx 1 root 10 Dec 11 14:18 ata-HDS728080PLA380_40Y9028LEN_PFDB32S7S44XLM-part5 -> ../../sda5",
          "lrwxrwxrwx 1 root  9 Dec 11 14:18 ata-TSSTcorpDVD-ROM_TS-H352C -> ../../sr0",
          "lrwxrwxrwx 1 root  9 Jan  4 15:01 usb-MBED_FDi_sk_A000000001-0:0 -> ../../sdc",
          "lrwxrwxrwx 1 root  9 Jan  5 07:47 usb-MBED_microcontroller_02400201489A1E6CB564E3D4-0:0 -> ../../sde",
          "lrwxrwxrwx 1 root  9 Jan  4 15:01 usb-MBED_microcontroller_0240020152986E5EAF6693E6-0:0 -> ../../sdb",
          "lrwxrwxrwx 1 root  9 Jan  5 07:49 usb-MBED_microcontroller_0240020152A06E54AF5E93EC-0:0 -> ../../sdf",
          "lrwxrwxrwx 1 root  9 Jan  5 07:47 usb-MBED_microcontroller_0672FF485649785087171742-0:0 -> ../../sdd",
          "lrwxrwxrwx 1 root  9 Dec 11 14:18 wwn-0x5000cca30ccffb77 -> ../../sda",
          "lrwxrwxrwx 1 root 10 Dec 11 14:18 wwn-0x5000cca30ccffb77-part1 -> ../../sda1",
          "lrwxrwxrwx 1 root 10 Dec 11 14:18 wwn-0x5000cca30ccffb77-part2 -> ../../sda2",
          "lrwxrwxrwx 1 root 10 Dec 11 14:18 wwn-0x5000cca30ccffb77-part5 -> ../../sda5"
        ]

        self.serial_list_2 = [
          "total 0",
          "lrwxrwxrwx 1 root 13 Jan  5 07:47 usb-MBED_MBED_CMSIS-DAP_02400201489A1E6CB564E3D4-if01 -> ../../ttyACM3",
          "lrwxrwxrwx 1 root 13 Jan  4 15:01 usb-MBED_MBED_CMSIS-DAP_0240020152986E5EAF6693E6-if01 -> ../../ttyACM1",
          "lrwxrwxrwx 1 root 13 Jan  5 07:49 usb-MBED_MBED_CMSIS-DAP_0240020152A06E54AF5E93EC-if01 -> ../../ttyACM4",
          "lrwxrwxrwx 1 root 13 Jan  4 15:01 usb-MBED_MBED_CMSIS-DAP_A000000001-if01 -> ../../ttyACM0",
          "lrwxrwxrwx 1 root 13 Jan  5 07:47 usb-STMicroelectronics_STM32_STLink_0672FF485649785087171742-if02 -> ../../ttyACM2"
        ]

        self.mount_list_2 = [
          "/dev/sdb on /media/usb0 type vfat (rw,noexec,nodev,sync,noatime,nodiratime,gid=1000,uid=1000,dmask=000,fmask=000)",
          "/dev/sdc on /media/usb1 type vfat (rw,noexec,nodev,sync,noatime,nodiratime,gid=1000,uid=1000,dmask=000,fmask=000)",
          "/dev/sdd on /media/usb2 type vfat (rw,noexec,nodev,sync,noatime,nodiratime,gid=1000,uid=1000,dmask=000,fmask=000)",
          "/dev/sde on /media/usb3 type vfat (rw,noexec,nodev,sync,noatime,nodiratime,gid=1000,uid=1000,dmask=000,fmask=000)",
          "/dev/sdf on /media/usb4 type vfat (rw,noexec,nodev,sync,noatime,nodiratime,gid=1000,uid=1000,dmask=000,fmask=000)"
        ]

        self.disk_list_3 = [
            "total 0",
            "lrwxrwxrwx 1 root 13 Jan  5 09:41 usb-MBED_MBED_CMSIS-DAP_0240020152986E5EAF6693E6-if01 -> ../../ttyACM0",
            "lrwxrwxrwx 1 root 13 Jan  5 10:00 usb-MBED_MBED_CMSIS-DAP_0240020152A06E54AF5E93EC-if01 -> ../../ttyACM3",
            "lrwxrwxrwx 1 root 13 Jan  5 10:00 usb-MBED_MBED_CMSIS-DAP_107002001FE6E019E2190F91-if01 -> ../../ttyACM1",
            "lrwxrwxrwx 1 root 13 Jan  5 10:00 usb-STMicroelectronics_STM32_STLink_0672FF485649785087171742-if02 -> ../../ttyACM2",
        ]

        self.serial_list_3 = [
            "total 0",
            "lrwxrwxrwx 1 root  9 Dec 11 14:18 ata-HDS728080PLA380_40Y9028LEN_PFDB32S7S44XLM -> ../../sda",
            "lrwxrwxrwx 1 root 10 Dec 11 14:18 ata-HDS728080PLA380_40Y9028LEN_PFDB32S7S44XLM-part1 -> ../../sda1",
            "lrwxrwxrwx 1 root 10 Dec 11 14:18 ata-HDS728080PLA380_40Y9028LEN_PFDB32S7S44XLM-part2 -> ../../sda2",
            "lrwxrwxrwx 1 root 10 Dec 11 14:18 ata-HDS728080PLA380_40Y9028LEN_PFDB32S7S44XLM-part5 -> ../../sda5",
            "lrwxrwxrwx 1 root  9 Dec 11 14:18 ata-TSSTcorpDVD-ROM_TS-H352C -> ../../sr0",
            "lrwxrwxrwx 1 root  9 Jan  5 09:41 usb-MBED_microcontroller_0240020152986E5EAF6693E6-0:0 -> ../../sdb",
            "lrwxrwxrwx 1 root  9 Jan  5 10:00 usb-MBED_microcontroller_0240020152A06E54AF5E93EC-0:0 -> ../../sde",
            "lrwxrwxrwx 1 root  9 Jan  5 10:00 usb-MBED_microcontroller_0672FF485649785087171742-0:0 -> ../../sdd",
            "lrwxrwxrwx 1 root  9 Jan  5 10:00 usb-MBED_microcontroller_107002001FE6E019E2190F91-0:0 -> ../../sdc",
            "lrwxrwxrwx 1 root  9 Dec 11 14:18 wwn-0x5000cca30ccffb77 -> ../../sda",
            "lrwxrwxrwx 1 root 10 Dec 11 14:18 wwn-0x5000cca30ccffb77-part1 -> ../../sda1",
            "lrwxrwxrwx 1 root 10 Dec 11 14:18 wwn-0x5000cca30ccffb77-part2 -> ../../sda2",
            "lrwxrwxrwx 1 root 10 Dec 11 14:18 wwn-0x5000cca30ccffb77-part5 -> ../../sda5",
        ]

        self.disk_list_4 = [
            "lrwxrwxrwx 1 root root   9 Mar 31 02:43 ata-VMware_Virtual_SATA_CDRW_Drive_00000000000000000001 -> ../../sr0",
            "lrwxrwxrwx 1 root root   9 Mar 31 02:43 ata-VMware_Virtual_SATA_CDRW_Drive_01000000000000000001 -> ../../sr1",
            "lrwxrwxrwx 1 root root   9 Apr  6 02:56 usb-MBED_VFS_0240000033514e45001f500585d40014e981000097969900-0:0 -> ../../sdb"
        ]

        self.serial_list_4 = [
            "lrwxrwxrwx 1 root root 13 Apr  6 02:56 pci-ARM_DAPLink_CMSIS-DAP_0240000033514e45001f500585d40014e981000097969900-if01 -> ../../ttyACM0"
        ]

        self.mount_list_4 = [
            "/dev/sdb on /media/przemek/DAPLINK type vfat (rw,nosuid,nodev,relatime,uid=1000,gid=1000,fmask=0022,dmask=0022,codepage=437,iocharset=iso8859-1,shortname=mixed,showexec,utf8,flush,errors=remount-ro,uhelper=udisks2)"
        ]

    def tearDown(self):
        pass

    def test_os_support(self):
        self.assertIn("LinuxGeneric", self.linux_generic.os_supported)

    def test_get_mount_point_basic(self):
        self.assertEqual('/media/usb0', self.linux_generic.get_mount_point('sdb', self.vfat_devices))
        self.assertEqual('/media/usb2', self.linux_generic.get_mount_point('sdd', self.vfat_devices))
        self.assertEqual('/media/usb3', self.linux_generic.get_mount_point('sde', self.vfat_devices))
        self.assertEqual('/media/usb1', self.linux_generic.get_mount_point('sdc', self.vfat_devices))

    def test_get_mount_point_ext(self):
        self.assertEqual('/media/MBED_xxx', self.linux_generic.get_mount_point('sdb', self.vfat_devices_ext))
        self.assertEqual('/media/MBED___x', self.linux_generic.get_mount_point('sdd', self.vfat_devices_ext))
        self.assertEqual('/media/MBED-xxx', self.linux_generic.get_mount_point('sde', self.vfat_devices_ext))
        self.assertEqual('/media/MBED_x-x', self.linux_generic.get_mount_point('sdc', self.vfat_devices_ext))

        self.assertEqual('/mnt/NUCLEO', self.linux_generic.get_mount_point('sda', self.vfat_devices_ext))
        self.assertEqual('/mnt/NUCLEO_', self.linux_generic.get_mount_point('sdf', self.vfat_devices_ext))
        self.assertEqual('/mnt/DAPLINK', self.linux_generic.get_mount_point('sdg', self.vfat_devices_ext))
        self.assertEqual('/mnt/DAPLINK_', self.linux_generic.get_mount_point('sdh', self.vfat_devices_ext))
        self.assertEqual('/mnt/DAPLINK__', self.linux_generic.get_mount_point('sdi', self.vfat_devices_ext))

    def test_get_dev_name(self):
        # With USB- prefix
        self.assertEqual('ttyACM0', self.linux_generic.get_dev_name('usb-MBED_MBED_CMSIS-DAP_02400201489A1E6CB564E3D4-if01 -> ../../ttyACM0'))
        self.assertEqual('ttyACM2', self.linux_generic.get_dev_name('usb-STMicroelectronics_STM32_STLink_0672FF485649785087171742-if02 -> ../../ttyACM2'))
        self.assertEqual('ttyACM3', self.linux_generic.get_dev_name('usb-MBED_MBED_CMSIS-DAP_0240020152986E5EAF6693E6-if01 -> ../../ttyACM3'))
        self.assertEqual('ttyACM2', self.linux_generic.get_dev_name('/dev/ttyACM2'))
        self.assertEqual('sdb', self.linux_generic.get_dev_name('usb-MBED_microcontroller_02400201489A1E6CB564E3D4-0:0 -> ../../sdb'))
        self.assertEqual('sde', self.linux_generic.get_dev_name('usb-MBED_microcontroller_0240020152986E5EAF6693E6-0:0 -> ../../sde'))
        self.assertEqual('sdd', self.linux_generic.get_dev_name('usb-MBED_microcontroller_0672FF485649785087171742-0:0 -> ../../sdd'))
        self.assertEqual('sdb', self.linux_generic.get_dev_name('usb-MBED_VFS_0240000033514e45001f500585d40014e981000097969900-0:0 -> ../../sdb'))
        # With PCI- prefix
        self.assertEqual('ttyACM0', self.linux_generic.get_dev_name('pci-ARM_DAPLink_CMSIS-DAP_0240000033514e45001f500585d40014e981000097969900-if01 -> ../../ttyACM0'))

    def test_get_detected_1_k64f(self):
        # get_detected(self, tids, disk_list, serial_list, mount_list)

        mbed_det = self.linux_generic.get_detected(self.tids,
            self.disk_list_1,
            self.serial_list_1,
            self.mount_list_1)

        self.assertEqual(1, len(mbed_det))
        self.assertIn([
            "FRDM_K64F",
            "sdb",
            "/media/usb0",
            "/dev/ttyACM1",
            "usb-MBED_microcontroller_0240020152986E5EAF6693E6-0:0 -> ../../sdb"
          ],
          mbed_det)

    def test_get_not_detected_1_unknown_lpc1768(self):
        # LPC1768 with weird target id like this:
        mbed_ndet = self.linux_generic.get_not_detected(self.tids,
            self.disk_list_1,
            self.serial_list_1,
            self.mount_list_1)

        self.assertEqual(1, len(mbed_ndet))
        self.assertIn([
            None,
            "sdc",
            "/media/usb1",
            "/dev/ttyACM0",
            "usb-MBED_FDi_sk_A000000001-0:0 -> ../../sdc"
          ],
          mbed_ndet)

    def test_get_detected_2_k64f(self):
        # get_detected(self, tids, disk_list, serial_list, mount_list)

        mbed_det = self.linux_generic.get_detected(self.tids,
            self.disk_list_2,
            self.serial_list_2,
            self.mount_list_2)

        self.assertEqual(3, len(mbed_det))
        self.assertIn([
            "FRDM_K64F",
            "sdf",
            "/media/usb4",
            "/dev/ttyACM4",
            "usb-MBED_microcontroller_0240020152A06E54AF5E93EC-0:0 -> ../../sdf"
          ],
          mbed_det)

        self.assertIn([
            "FRDM_K64F",
            "sde",
            "/media/usb3",
            "/dev/ttyACM3",
            "usb-MBED_microcontroller_02400201489A1E6CB564E3D4-0:0 -> ../../sde"
          ],
          mbed_det)

        self.assertIn([
            "FRDM_K64F",
            "sdb",
            "/media/usb0",
            "/dev/ttyACM1",
            "usb-MBED_microcontroller_0240020152986E5EAF6693E6-0:0 -> ../../sdb"
          ],
          mbed_det)

    def test_get_detected_2_k64f(self):
        # get_detected(self, tids, disk_list, serial_list, mount_list)

        mbed_det = self.linux_generic.get_detected(self.tids,
            self.disk_list_4,
            self.serial_list_4,
            self.mount_list_4)

        self.assertEqual(1, len(mbed_det))
        self.assertIn([
            "FRDM_K64F",
            "sdb",
            "/media/przemek/DAPLINK",
            "/dev/ttyACM0",
            "usb-MBED_VFS_0240000033514e45001f500585d40014e981000097969900-0:0 -> ../../sdb"
          ],
          mbed_det)

    def test_get_not_detected_2_unknown_lpc1768_stf401(self):
        # LPC1768 with weird target id like this:
        mbed_ndet = self.linux_generic.get_not_detected(self.tids,
            self.disk_list_2,
            self.serial_list_2,
            self.mount_list_2)

        self.assertEqual(2, len(mbed_ndet))

        self.assertIn([
            None,
            "sdc",
            "/media/usb1",
            "/dev/ttyACM0",
            "usb-MBED_FDi_sk_A000000001-0:0 -> ../../sdc"
          ],
          mbed_ndet)

        self.assertIn([
            None,
            "sdd",
            "/media/usb2",
            "/dev/ttyACM2",
            "usb-MBED_microcontroller_0672FF485649785087171742-0:0 -> ../../sdd"
          ],
          mbed_ndet)

    def test_get_disk_hex_ids_1(self):
        disk_hex_ids = self.linux_generic.get_disk_hex_ids(self.disk_list_1)
        self.assertEqual(2, len(disk_hex_ids))

        hex_keys = disk_hex_ids.keys()
        self.assertEqual(2, len(hex_keys))
        self.assertIn("A000000001", hex_keys)
        self.assertIn("0240020152986E5EAF6693E6", hex_keys)

        hex_values = disk_hex_ids.values()
        self.assertEqual(2, len(hex_values))
        self.assertIn("usb-MBED_FDi_sk_A000000001-0:0 -> ../../sdc", hex_values)
        self.assertIn("usb-MBED_microcontroller_0240020152986E5EAF6693E6-0:0 -> ../../sdb", hex_values)

    def test_get_rpi_disk_hex_ids_1(self):
        disk_hex_ids = self.linux_generic.get_disk_hex_ids(self.disk_list_rpi_1)
        self.assertEqual(6, len(disk_hex_ids))

        hex_keys = disk_hex_ids.keys()
        self.assertEqual(6, len(hex_keys))
        self.assertIn("0240000028634e4500135006691700105f21000097969900", hex_keys)
        self.assertIn("0240000028884e450018700f6bf000338021000097969900", hex_keys)
        self.assertIn("0240000028884e45001f700f6bf000118021000097969900", hex_keys)
        self.assertIn("0240000028884e450036700f6bf000118021000097969900", hex_keys)
        self.assertIn("0240000029164e45001b0012706e000df301000097969900", hex_keys)
        self.assertIn("0240000029164e45002f0012706e0006f301000097969900", hex_keys)

        hex_values = disk_hex_ids.values()
        self.assertEqual(6, len(hex_values))
        self.assertIn("usb-MBED_VFS_0240000028634e4500135006691700105f21000097969900-0:0 -> ../../sdb", hex_values)
        self.assertIn("usb-MBED_VFS_0240000028884e450018700f6bf000338021000097969900-0:0 -> ../../sdc", hex_values)
        self.assertIn("usb-MBED_VFS_0240000028884e45001f700f6bf000118021000097969900-0:0 -> ../../sdd", hex_values)
        self.assertIn("usb-MBED_VFS_0240000028884e450036700f6bf000118021000097969900-0:0 -> ../../sde", hex_values)
        self.assertIn("usb-MBED_VFS_0240000029164e45001b0012706e000df301000097969900-0:0 -> ../../sdd", hex_values)
        self.assertIn("usb-MBED_VFS_0240000029164e45002f0012706e0006f301000097969900-0:0 -> ../../sdc", hex_values)

    def test_get_disk_hex_ids_2(self):
        disk_hex_ids = self.linux_generic.get_disk_hex_ids(self.disk_list_2)
        self.assertEqual(5, len(disk_hex_ids))

        # Checking for scanned target ids (in dict keys)
        hex_keys = disk_hex_ids.keys()
        self.assertEqual(5, len(hex_keys))
        self.assertIn("A000000001", hex_keys)
        self.assertIn("0240020152A06E54AF5E93EC", hex_keys)
        self.assertIn("0672FF485649785087171742", hex_keys)
        self.assertIn("02400201489A1E6CB564E3D4", hex_keys)
        self.assertIn("0240020152986E5EAF6693E6", hex_keys)

        hex_values = disk_hex_ids.values()
        self.assertEqual(5, len(hex_values))
        self.assertIn("usb-MBED_FDi_sk_A000000001-0:0 -> ../../sdc", hex_values)
        self.assertIn("usb-MBED_microcontroller_0240020152A06E54AF5E93EC-0:0 -> ../../sdf", hex_values)
        self.assertIn("usb-MBED_microcontroller_0672FF485649785087171742-0:0 -> ../../sdd", hex_values)
        self.assertIn("usb-MBED_microcontroller_02400201489A1E6CB564E3D4-0:0 -> ../../sde", hex_values)
        self.assertIn("usb-MBED_microcontroller_0240020152986E5EAF6693E6-0:0 -> ../../sdb", hex_values)

    def test_get_disk_hex_ids_4(self):
        disk_hex_ids = self.linux_generic.get_disk_hex_ids(self.disk_list_4)
        self.assertEqual(1, len(disk_hex_ids))

        # Checking for scanned target ids (in dict keys)
        hex_keys = disk_hex_ids.keys()
        self.assertIn("0240000033514e45001f500585d40014e981000097969900", hex_keys)

        hex_values = disk_hex_ids.values()
        self.assertIn("usb-MBED_VFS_0240000033514e45001f500585d40014e981000097969900-0:0 -> ../../sdb", hex_values)

    def test_get_dev_by_id_process_ret_0(self):
        id_disks = self.linux_generic.get_dev_by_id_process(self.disk_list_3, 0)
        id_serial = self.linux_generic.get_dev_by_id_process(self.serial_list_3, 0)

        self.assertEqual(4, len(id_disks))
        self.assertEqual(13, len(id_serial))
        self.assertNotIn("total 0", id_disks)
        self.assertNotIn("Total 0", id_disks)
        self.assertNotIn("total 0", id_serial)
        self.assertNotIn("Total 0", id_serial)

    def test_get_dev_by_id_process_ret_non_zero(self):
        id_disks = self.linux_generic.get_dev_by_id_process(self.disk_list_3, -1)
        id_serial = self.linux_generic.get_dev_by_id_process(self.serial_list_3, -1)

        self.assertEqual([], id_disks)
        self.assertEqual([], id_serial)


if __name__ == '__main__':
    unittest.main()
