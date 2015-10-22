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

### install sssd
    yum install -y sssd

### install authconfig
    yum install -y authconfig

### configure sssd (copy and paste this whole section)
    cat >/etc/sssd/sssd.conf<<EOF
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
    ldap_search_base = dc=vbi,dc=vt,dc=edu
    chpass_provider = ldap
    id_provider = ldap
    ldap_uri = ldap://ldap2.vbi.vt.edu
    ldap_tls_cacertdir = /etc/openldap/cacerts
    ldap_schema = rfc2307
    access_provider=ldap
    ldap_access_order = expire
    ldap_account_expire_policy = shadow
    EOF

### set proper perms
    chmod 600 /etc/sssd/sssd.conf

### nasty hack #1
    mkdir -p /etc/openldap/cacerts

### configure the rest of auth mechanisms, including the download of our CA cert
    authconfig --nostart --enablesssd --enablesssdauth --enablelocauthorize --update --ldaploadcacert=http://cert.vbi.vt.edu/vbi-cacert.pem

### nasty hack #2, not sure why manual authconfig doesn't create it
    ln -sf /etc/openldap/cacerts/authconfig_downloaded.pem /etc/openldap/cacerts/3a5608b0.0

### finally, update and restart. we also enable creation of home dirs for new users
    authconfig --enablemkhomedir --update

### for some reason on newer centos systems, --enablesssd does not work as it used to, so we have to manually start sssd
    chkconfig sssd on
    service sssd start

### check if it's working
    # getent passwd
