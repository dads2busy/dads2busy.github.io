---
layout: post
category: "tools"
subcategory: "Bash Scripts"
title: "MountThisSSH - Remote Mount with SSHFS"
ordinal: 3
date: 2015-10-22 16:25:06 -0700
comments: true
website: ""
---
<!--break-->
### A Remote Volume Mounting Script for Linux and Mac
#### This script reads from the ssh shortcuts in your ~/.ssh/config file. rmount will automatically create the mount folder and mount the remote filesystem to the folder. rumount will unmount the remote filesystem.
#### Add this code or a link to the script file in your .bashrc file

    #!/bin/bash -ex
    # MountThisSSH - Remote Mount (sshfs)
    # creates mount folder and mounts the remote filesystem
    # created by Aaron D. Schroeder as an enhanced version of a script originally created by Brett Terpstra.

    rmount() {
      if [[ $(df | grep $1 | wc -l) -eq 0 ]]; then
    	  OS=$(uname -s)
    	  local host folder mname
    	  host="${1%%:*}:"
    	  [[ ${1%:} == ${host%%:*} ]] && folder='' || folder=${1##*:}
    	  if [[ $2 ]]; then
    	    mname=$2
    	  else
    	    mname=${folder##*/}
    	    [[ "$mname" == "" ]] && mname=${host%%:*}
    	  fi

    	  if [[ $(grep -i "host ${host%%:*}" ~/.ssh/config) != '' ]]; then
    	    mkdir -p ~/mounts/$mname > /dev/null
    	    if [[ $OS == 'Linux' ]]; then
    	    	sshfs $host$folder ~/mounts/$mname -oauto_cache,reconnect,follow_symlinks -o IdentityFile=~/.ssh/id_rsa && echo "mounted ~/mounts/$mname"
    	    fi
    	    if [[ $OS == 'Darwin' ]]; then
    	    	sshfs $host$folder ~/mounts/$mname -oauto_cache,reconnect,defer_permissions,negative_vncache,volname=$mname,noappledouble,follow_symlinks -o IdentityFile=~/.ssh/id_rsa && echo "mounted ~/mounts/$mname"
    	    fi
    	  else
    	    echo "No entry found for ${host%%:*}"
    	    return 1
    	  fi
      else
      	  echo "already mounted";
      fi
    }

    # Remote Umount, unmounts and deletes local folder (experimental, watch you step)
    rumount() {
      if [[ $1 == "-a" ]]; then
        ls -1 ~/mounts/|while read dir
        do
          [[ $(mount | grep "mounts/$dir") ]] && umount ~/mounts/$dir
          [[ $(ls ~/mounts/$dir) ]] || rm -rf ~/mounts/$dir
        done
      else
        [[ $(mount | grep "mounts/$1") ]] && umount ~/mounts/$1
        [[ $(ls ~/mounts/$1) ]] || rm -rf ~/mounts/$1
      fi
    }
