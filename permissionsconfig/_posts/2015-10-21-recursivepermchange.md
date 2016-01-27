---
layout: post
category: "serverconfig"
subcategory: "Permissions"
title: "Recursive Folder and File Permission Change"
ordinal: 2
date: 2015-10-22 16:25:06 -0700
comments: true
website: ""
---
<!--break-->

###To recursively give directories read&execute privileges:
    find /path/to/base/dir -type d -exec chmod 770 {} +

###To recursively give files read privileges:
    find /path/to/base/dir -type f -exec chmod 660 {} +
