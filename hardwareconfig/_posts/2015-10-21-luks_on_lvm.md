---
layout: post
category: "serverconfig"
subcategory: "Hardware Configuration"
title: "LUKS on LVM"
ordinal: 1
date: 2015-10-21 16:25:06 -0700
comments: true
---
<!--break-->

## 1. Create a LUKS Encrypted Logical Volume
(assuming you already have a volume group set up)
### Create Logical Volume
    # lvcreate -L [new logical volume size] [volume group name] -n [new logical volume name]
    example
    # lvcreate -L 100G myVolGroup -n myLogVol1

### Format the new logical volume
    # mkfs.ext4 /dev/mapper/[volume group name]_[new logical volume name]
    example
    # mkfs.ext4 /dev/mapper/myVolGroup_myLogVol1

### Fill formatted logical volume with random Data
    # dd if = /dev/urandom of=/dev/[volume group name]/[new logical volume name]
    example
    # dd if = /dev/urandom of=/dev/myVolGroup/myLogVol1

### Create encrypted layer for the new logical volume
    # cryptsetup luksformat -c -aes-xts-plain64 -s 512 /dev/[volume group name]/[new logical volume name]
    example
    cryptsetup luksformat -c -aes-xts-plain64 -s 512 /dev/myVolGroup/myLogVol1

### Create a combined logical volume + encrypted layer
    # cryptsetup open --type luks /dev/[volume group name]/[new logical volume name] [new combined logical volume + encryption layer name]
    example
    # cryptsetup open --type luks /dev/myVolGroup/myLogVol1 myLogVol1_Encrypted

### Format the combined logical volume + encryption layer
    # mkfs.ext4 /dev/mapper/[new combined logical volume + encryption layer name]
    example
    # mkfs.ext4 /dev/mapper/myLogVol1_Encrypted

### Mount the newly formatted combined logical volume + encryption layer
    # mount /dev/mapper/[new combined logical volume + encryption layer name] /path/to/mount/folder
    example
    # mount /dev/mapper/myLogVol1_Encrypted /home/auser/myEncryptedVolume

## 2. Automount the Encrypted Volume on Boot
### Create a random keyfile
    # dd if=/dev/urandom of=/etc/luks-keys bs=1 count=256

### Make the keyfile read-only to root
    # chmod 0400 /etc/luks-keys

### Add the keyfile to LUKS
    # cryptsetup luksAddKey /dev/[volume group name]/[new logical volume name] /etc/luks-keys/[new logical volume name]
    example
    # cryptsetup luksAddKey /dev/myVolGroup/myLogVol1 /etc/luks-keys/myLogVol1

You'll be prompted to enter an (existing) password to unlock the drive. If everything works well, you should get an output like this:
    Enter any LUKS passphrase:
    key slot 0 unlocked.
    Command successful.

### Open /etc/crypttab to create a mapper that can then be referenced in the fstab
    # nano /etc/crypttab
    add an entry like:
    # [name of the mapper]    /dev/[volume group name]/[new logical volume name]    /etc/luks-keys/myLogVol1    luks
    example
    # myLogVol1_crypt    /dev/myVolGroup/myLogVol1    /etc/luks-keys/myLogVol1    luks

### Mount the device in fstab
    # nano /etc/fstab
    add an entry like:
    # /dev/mapper/[name of the mapper]  [mount point]   [filesystem]  defaults        0 2
    example
    /dev/mapper/myLogVol1_crypt  /home/myLogVol1   ext4  defaults        0 2
Make sure you have the correct mapper name created in the previous step and that the mount point/folder exists.

### Reboot or remount
    to remount you'll have to reload the cryptab before issuing the mount command, like:
    # systemctl daemon-reload
    # systemctl restart cryptsetup.target
    # mount -a
