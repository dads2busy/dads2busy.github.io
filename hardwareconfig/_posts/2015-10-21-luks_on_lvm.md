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

(assuming you already have a volume group set up)
### Create Logical Volume
    # lvcreate -L <new logical volume size> <volume group name> -n <new logical volume name>
    example
    # lvcreate -L 100G myVolGroup -n myLogVol1

### Format the new logical volume
    # mkfs.ext4 /dev/mapper/<volume group name>_<new logical volume name>
    example
    # mkfs.ext4 /dev/mapper/myVolGroup_myLogVol1

### Fill formatted logical volume with random Data
    # dd if = /dev/urandom of=/dev/<volume group name>/<new logical volume name>
    example
    # dd if = /dev/urandom of=/dev/myVolGroup/myLogVol1

### Create encrypted layer for the new logical volume
    # cryptsetup luksformat -c -aes-xts-plain64 -s 512 /dev/<volume group name>/<new logical volume name>
    example
    cryptsetup luksformat -c -aes-xts-plain64 -s 512 /dev/myVolGroup/myLogVol1

### Create a combined logical volume + encrypted layer
    # cryptsetup open --type luks /dev/<volume group name>/<new logical volume name> <new combined logical volume + encryption layer name>
    example
    # cryptsetup open --type luks /dev/myVolGroup/myLogVol1 myLogVol1_Encrypted

### Format the combined logical volume + encryption layer
    # mkfs.ext4 /dev/mapper/<new combined logical volume + encryption layer name>
    example
    # mkfs.ext4 /dev/mapper/myLogVol1_Encrypted

### Mount the newly formatted combined logical volume + encryption layer
    # mount /dev/mapper/<new combined logical volume + encryption layer name> /path/to/mount/folder
    example
    # mount /dev/mapper/myLogVol1_Encrypted /home/auser/myEncryptedVolume
