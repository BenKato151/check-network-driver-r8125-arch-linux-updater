# Check Network Driver for RTL8125 2.5GbE Controller - Arch Linux

I had this https://bbs.archlinux.org/viewtopic.php?id=257114 problem and 
this https://bbs.archlinux.org/viewtopic.php?pid=1917633#p1917633 solution helped me.

I wrote that script because I needed to compile and reinstall the network-driver everytime I updated my linux kernels (linux, linux-lts, zen).
This script works only on an already installed system. 

You can clone this project and with `python3 update-network-driver-r8125.py` it will install the r8125 network driver.
Or you can put this folder in your `~/.bashrc`, `chmod +x update-network-driver-r8125.py` and just run it like any other script.

Here is a guide if you are on a live-iso and your network-driver isn't loaded.
 
Because I had no internet connection I booted Arch from another USB on my laptop and used an external SSD.
(Or you can boot Windows and do all this in a vm if you don't have another devices.)
Follow these steps (the disk mount part is for both machines):

1. **Mount Disk device**
    - `fdisk -l` To find my external SSD and the right partition. Remember where it it located (e.g. `/dev/sde1`) 
    - `nano /etc/fstab` and write in that `/dev/[your device-partition]   [Path like /media/ssd]  auto    auto    0   0`
    - `mkdir [path where you want to mount like /media/ssd]` and `mount [your device-partition] [path]` To mount and use the external ssd
    
2. **Download and compile on laptop with working network connection**
    - `pacman -S git gcc make fakeroot curl` Download the necessary dependencies
    - `useradd -G wheel -s /bin/bash username` to create non root user
    - `EDITOR=nano visudo` uncomment the line `%wheel ALL=(ALL) ALL` and save to be sudo
    - `su username && sudo mkdir /tmp/driver && cd /tmp/driver` change user to non root
    - `git clone https://aur.archlinux.org/r8125.git && cd r8125/` Download the network driver, change dir
    - `makepkg` to compile
    - `sudo cp ./r8125-9.003.05-1-x86_64.pkg.tar.zst [ssd path and a directory]` to copy the installation package to ssd.
    - To be save, download a linux-header package for your version
        - `uname -r` to check your kernel version. Remember that.
        - `curl -L -O [URL]` You need to find the right linux-headers version for your kernel. 
            Just google `linux-headers [or linux-lts-headers if you want] [kernel version] archive` and type the whole damn URL to that .zst 
        - `sudo cp ./[linux-headers-version.pkg.tar.zst] [ssd path and a directory]` copy this to ssd too
        - `pacman -U ./[linux-headers-version.pkg.tar.zst]` to install it for the next step
    
3. **Install package on non-working-live-machine**
    - Do step 1 here too
    - `mkdir /tmp/r8125 && cp [ssd path]/r8125-9.003.05-1-x86_64.pkg.tar.zst /tmp/r8125` 
    - `cp [ssd path]/[linux-headers-version.pkg.tar.zst] /tmp/r8125 && cd /tmp/r8125` copy installation packages to machine
    - `pacman -U ./[linux-headers-version.pkg.tar.zst]` Install the linux-headers before the network driver
    - `pacman -U ./r8125-9.003.05-1-x86_64.pkg.tar.zst` Install the network driver finally
    - `lspci -vv` to check which network driver is currently loaded and disable it with `rmmod [wrong_module]`
    - `modprobe r8125` activate the new module manually
    - Now you should install your main system until you reboot into it.

4. **Install package on installed arch-machine**

    After you installed your main system you will that the network driver wasn't loaded.
    You need to do step 3 again with some steps afterwards:
    - `sudo bash -c 'echo "blacklist [wrong_module]" > /etc/modprobe.d/[wrong_module].conf'` blacklist the wrong module from boot
    - `sudo bash -c 'echo "r8125" > /etc/modules-load.d/r8125.cfg'` Only forces the module to load on boot
    - `sudo reboot` reboot to check if the module is loaded
