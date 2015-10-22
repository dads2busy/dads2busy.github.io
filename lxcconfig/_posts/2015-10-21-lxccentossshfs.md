---
layout: post
category: "serverconfig"
subcategory: "LXC Configuration"
title: "LXC SSHFS Setup (Centos 7)"
ordinal: 2
date: 2015-10-22 16:25:06 -0700
comments: true
---
<!--break-->

### SSH into the LXC Container
    # ssh <root@the.conatiner.ip.address>

### Install wget
    # yum install wget -y

### Add the EPEL Repository
    ## RHEL/CentOS 7 64-Bit ##
    # wget http://dl.fedoraproject.org/pub/epel/7/x86_64/e/epel-release-7-5.noarch.rpm
    # rpm -ivh epel-release-7-5.noarch.rpm

### Install nano
    # yum install nano -y

### Install SSHFS
    # yum install SSHFS -y

#### You won't be able to use SSHFS initially. The LXC container does not automatically created all needed device nodes, like the fuse device node needed by SSHFS. Therefore, we need to create both a script to create the node and a systemd unit file that will run the script on boot.

### Create a script file that creates a fuse device node
    # cd /root
    # nano fuse-mknod.sh
In the script file, enter the following:

    #!/usr/bin/env bash

    # creates a node for fuse devices
    mknod -m 666 /dev/fuse c 10 229

### Make the script executable
    # chmod +x fuse-mknod.sh

### Create a systemd unit file to launch the script
    # nano /usr/lib/systemd/system/fuse-mknod.service
In the unit file, enter the following:

    [Unit]
    Description=Make Fuse Device Node Service
    After=network.target

    [Service]
    Type=simple
    ExecStart=/root/fuse-mknod.sh
    Restart=on-abort

    [Install]
    WantedBy=multi-user.target

### Set the unit file to run at boot
    # systemctl enable fuse-mknod.service

### Reboot the container and try to use SSHFS
