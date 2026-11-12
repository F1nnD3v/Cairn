# Install Cairn in VMware Workstation

VMware Workstation Pro is free for personal use and handles KDE's 3D graphics better than
VirtualBox. Cairn already includes VMware's guest tools, so window resizing and copy-paste
between Windows and Cairn work without extra setup.

Download it from Broadcom's support portal (it asks you to create a free account once).

## 1. Get the installer ISO

Same as for VirtualBox: see [step 1 of the VirtualBox guide](install-virtualbox.md#1-download-the-installer-iso).

## 2. Create the virtual machine

1. **File → New Virtual Machine → Typical**.
2. Choose **I will install the operating system later**. This skips VMware's "Easy Install",
   which would try to answer the installer's questions itself.
3. **Guest operating system:** Linux, version **Other Linux 6.x kernel 64-bit**.
4. **Name:** `Cairn`. **Disk:** **64 GB**.
5. Click **Customize Hardware**:
   - **Memory:** 8 GB (4 GB minimum)
   - **Processors:** 4
   - **New CD/DVD:** *Use ISO image file* → pick `install.iso`
   - **Display:** tick **Accelerate 3D graphics**
6. Click **Finish**, then open **VM → Settings → Options → Advanced** and make sure
   **Firmware type** is **UEFI** (leave Secure Boot unticked).

## 3. Install and first start

Power on the VM and continue from [step 3 of the VirtualBox guide](install-virtualbox.md#3-install).
The installer, first start and updates are the same.

If the installer starts again after the reboot, disconnect the ISO:
**VM → Settings → CD/DVD → untick Connected**, then restart the VM.
