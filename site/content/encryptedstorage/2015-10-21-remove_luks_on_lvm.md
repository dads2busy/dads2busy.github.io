---
layout: post
category: "serverconfig"
subcategory: "Encrypted Storage"
title: "Remove LUKS on LVM Partition"
ordinal: 2
date: 2015-10-21 16:25:06 -0700
comments: true
website: ""
---
<!--break-->

[root@temp4 ~]# lvremove /dev/mapper/luks01vg-luks01lv<br />
  Logical volume luks01vg/luks01lv is used by another device.<br />
[root@temp4 ~]# umount /luks<br />
[root@temp4 ~]# cryptsetup luksClose /dev/mapper/luks1<br />
[root@temp4 ~]# lvremove /dev/mapper/luks01vg-luks01lv<br />
Do you really want to remove active logical volume luks01lv? [y/n]:
