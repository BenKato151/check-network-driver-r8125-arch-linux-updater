#!/usr/bin/python
from subprocess import check_output, Popen, call, PIPE
import os


def check_status():
    # Check version of current system and compares with file from last run
    # return None if they are equal or the new version, saved the new one in the file
    checked_version = check_output(['uname', '-r']).decode("utf-8")
    abspath = os.path.abspath(__file__)
    working_directory = os.path.dirname(abspath)
    os.chdir(working_directory)
    with open(f"./checked-version", "r") as versionFile:
        if str(versionFile.read()) == checked_version:
            updated_version = None
        else:
            updated_version = checked_version

    if updated_version is not None:
        with open("./checked-version", "w") as versionFile:
            versionFile.write(f"{checked_version}")

    return updated_version


def update_network_drivers(linux_version):
    # compile the network-driver, install it and activate it
    wd = os.getcwd()
    os.chdir(f"{wd}/r8125")
    write_new_pkgbuild(linux_version)
    subprocess_cmd("makepkg")
    subprocess_cmd("sudo pacman -U r8125-9.003.05-1-x86_64.pkg.tar.zst --noconfirm")
    subprocess_cmd("sudo modprobe r8125")
    call(["rm", "-rf", "pkg/"])
    call(["rm", "-rf", "src/"])
    call(["rm", "r8125-dkms-9.003.05-1-x86_64.pkg.tar.zst"])
    call(["rm", "r8125-9.003.05-1-x86_64.pkg.tar.zst"])
    os.chdir(wd)


def subprocess_cmd(command):
    # Helper function to print out the commands
    process = Popen(command, stdout=PIPE, shell=True)
    proc_stdout = process.communicate()[0].strip()
    print(proc_stdout.decode("utf-8"))


def write_new_pkgbuild(pkg_version):
    # read the PKGBUILD.bak file for compiling and write it in the final file with the newer version
    clean_pkg_version = pkg_version.replace('\n', "")
    with open("./PKGBUILD.bak", "r") as PKGBUILD_bak:
        with open("./PKGBUILD", "w") as PKGBUILD:
            PKGBUILD.write(PKGBUILD_bak.read().replace("_kernver='UPDATING_VERSION'",
                                                       f"_kernver='{clean_pkg_version}'"))


def write_configs():
    subprocess_cmd("sudo bash -c 'echo \"blacklist r8169\" > /etc/modprobe.d/r8169.conf'")
    subprocess_cmd("sudo bash -c 'echo \"r8125\" > /etc/modules-load.d/r8125.cfg'")


if __name__ == '__main__':
    # checks for input just in case. No really need for them, but I like it that way
    version = check_status()
    if version is None:
        print("No need for updating the Network Driver")
    else:
        print(f"Update {version} found.\nInstalling...\n")
        update_network_drivers(version)
        print("Finished... \nWrite config?")
        # write_configs()
