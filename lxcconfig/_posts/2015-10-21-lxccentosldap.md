---
layout: post
category: "serverconfig"
subcategory: "LXC Configuration"
title: "LDAP Authentication (Centos 7)"
ordinal: 3
date: 2015-10-22 16:25:06 -0700
comments: true
---
<!--break-->

### Install sssd
    # yum install sssd -y

### Install authconfig
    # yum install authconfig -y

### Configure sssd (copy and paste this whole section)
*Before using you will need to enter your organization's domain components and your ldap uri*

    # cat >/etc/sssd/sssd.conf<<EOF
      [sssd]
      config_file_version = 2
      reconnection_retries = 3

      sbus_timeout = 30
      services = nss, pam

      domains = default

      [nss]
      filter_groups = root
      filter_users = root
      reconnection_retries = 3

      [pam]
      reconnection_retries = 3

      [domain/default]
      ldap_id_use_start_tls = True
      cache_credentials = True
      auth_provider = ldap
      debug_level = 0
      enumerate = True
      ldap_search_base = [your domain components]
      chpass_provider = ldap
      id_provider = ldap
      ldap_uri = [your ldap uri]
      ldap_tls_cacertdir = /etc/openldap/cacerts
      ldap_schema = rfc2307
      access_provider=ldap
      ldap_access_order = expire
      ldap_account_expire_policy = shadow
      EOF

### Set proper permissions
    # chmod 600 /etc/sssd/sssd.conf

### Create the directory for cacerts
    # mkdir -p /etc/openldap/cacerts

### Configure the rest of auth mechanisms, including the download of your CA cert
*Before using you willl need to enter the uri to your organization's pem certificate*

    # authconfig --nostart --enablesssd --enablesssdauth --enablelocauthorize --update --ldaploadcacert=[the uri to your pem certificate]

### Create a necessary link
    # ln -sf /etc/openldap/cacerts/authconfig_downloaded.pem /etc/openldap/cacerts/3a5608b0.0

### Enable creation of home dirs for new users and update the config
    # authconfig --enablemkhomedir --update

### Set sssd to start at boot and the start sssd
    # systemctl enable sssd
    # systemctl start sssd

### Check if it's working
    # getent passwd
