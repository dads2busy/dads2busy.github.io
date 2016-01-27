---
layout: post
category: "serverconfig"
subcategory: "Permissions"
title: "Default Folder Permissions"
ordinal: 1
date: 2015-10-22 16:25:06 -0700
comments: true
website: ""
---
<!--break-->

###Make all new child folders be owned by same group
    chmod g+s <directory>  //set gid

###Set default permissions for new folders
    setfacl -d -m g::rwx /<directory>  //set group to rwx default
    setfacl -d -m o::rx /<directory>   //set other

###Verify Settings
    getfacl /<directory>
