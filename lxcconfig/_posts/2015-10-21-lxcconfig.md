---
layout: post
category: "serverconfig"
subcategory: "LXC Configuration"
title: "LXC Container Configuration"
ordinal: 3
date: 2015-10-22 16:25:06 -0700
comments: true
website: ""
---
<!--break-->
    # Template used to create this container: /usr/share/lxc/templates/lxc-centos
    # Parameters passed to the template:
    # For additional config options, please look at lxc.container.conf(5)

    # Location and name
    lxc.rootfs = /home/vms/lxc/analysis-server/rootfs
    lxc.utsname = analysis-server
    # Network
    lxc.network.type = veth
    lxc.network.link = virbr0
    lxc.network.flags = up
    # Memory - limit memory to 20GB
    lxc.cgroup.memory.limit_in_bytes = 20000M
    # Start on boot
    lxc.start.auto = 1
    # Include common configuration
    lxc.include = /usr/share/lxc/config/centos.common.conf
    lxc.arch = x86_64
    # When using LXC with apparmor, uncomment the next line to run unconfined:
    #lxc.aa_profile = unconfined
    # Mount host partitions
    lxc.mount.entry=/home/sdal/projects/mann home/sdal/projects/mann none bind,create=dir 0 0
    lxc.mount.entry=/home/sdal/mann2 home/sdal/projects/mann2 none bind,create=dir 0 0
    lxc.mount.entry=/home/sdal/projects/resinfra home/sdal/projects/resinfra none bind,create=dir 0 0
    lxc.mount.entry=/home/sdal/projects/arlington911 home/sdal/projects/arlington911 none bind,create=dir 0 0
    lxc.mount.entry=/home/sdal/projects/census home/sdal/projects/census none bind,create=dir 0 0
