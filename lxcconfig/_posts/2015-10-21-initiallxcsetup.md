---
layout: post
category: "serverconfig"
subcategory: "LXC Configuration"
title: "LXC Container Creation"
ordinal: 1
date: 2015-10-22 16:25:06 -0700
comments: true
website: ""
---
<!--break-->

### Create an LXC Container (Centos 7)
    # lxc-create -n <container name> -t <container type> [-p /path/to/where/stored]
    examples
    # lxc-create -n myContainer -t centos
    # lxc-create -n myContainer -t centos -p /home/containers

### Copy the password
The output from lcx-create includes a path to file containing the temporary password for the new container. Open the file and copy (or write down) the password.

#### IF you saved your container to somewhere other than the default path /var/lib/lxc, then you will need to symlink to the default location. Otherwise the lxc utilities, like lxc-start, won't be able to find the container.
    for example
    # ln -s /home/containers/myContainer /var/lib/lxc/myContainer

### Start the LXC Container
    # lxc-start -n myContainer

#### IF you get an error when starting the container, you might have to change the name of the virtual bridge. Default is "lxcvbr0" but, at least on Centos 7, the correct name is "virvbr0"
    # nano /var/lib/lxc/myContainer/config

    change lxc.network.link = lxcbr0 to lxc.network.link = virbr0

### Get LXC Container Info (including the IP address)
    # lxc-info -n myContainer

### SSH into the LXC Container
    # ssh <root@the.conatiner.ip.address>
When prompted, paste/enter the temporary password. You will be prompted to create a new root password.
