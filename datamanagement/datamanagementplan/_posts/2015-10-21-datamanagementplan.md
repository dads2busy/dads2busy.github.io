---
layout: post
category: "datamanagement"
subcategory: "Data Management Plan"
title: "Transfer, Storage, Access, and Destruction"
ordinal: 1
date: 2015-10-21 16:25:06 -0700
comments: true
---

##Transfer
All data sets transferred to SDAL are done so via encrypted means. For remote transfers, a certain set of network protocols are acceptable. Acceptable network protocols for remote data transfer include FTPS, SFTP, SCP, and WebDAV over HTTPS. The SDAL preferred remote transfer method is via an SFTP server temporary established for the purpose of the transfer. The SFTP server is deactivated after successful data transfer. The remote user is provided a temporary password for SFTP server access that is also deleted after successful data transfer. Data sets that are to be transferred manually (not via remote network connection) are transferred using an encrypted USB storage device employing, at a minimum, an EncFS-based encrypted file partition.

Email is not considered secure and is not used to transmit covered data unless additional file-level encryption tools, requested and approved by the data provider, are employed (e.g. gpg, ccrypt, 7zip using AES).

##Storage
The data for each SDAL research project is stored on a new project-dedicated encrypted Logical Volume Management (LVM) partition on on of our servers. The LVM partition is encrypted using Linux Unified Key Setup or LUKS. This setup is typically referred to as “LUKS-on-LVM”. LUKS is a disk-encryption specification that is based on an enhanced version of cryptsetup, using dm-crypt as the disk encryption backend. Each SDAL data server is housed within one of three highly-secure, high-performance computing (HPC) data centers located in the Virginia Bioinformatics Institute (VBI) in Blacksburg, VA and maintained by VBI Information and Technology Computing Services personnel. Direct access to data sets for loading and management purposes is restricted to project-approved PIs and data managers. The method of access for loading and management purposes is via SSH using RSA encrypted key pairs.

##Access
Copying of server-hosted data down to researcher workstations is not permitted.  All data set analyses and results are saved back to the server, not to the individual researcher's workstation. Originally provided data records are accessible via secured remote access only in a read-only format to authorized users. The intention is that original data sets are never modified. Resulting modified read-write data sets that are produced from the original data sets are also stored back to the server and only accessible via secured remote access. Unless special authorization is given, researchers do not have direct access to data files. Instead, data access is mediated by the use of different data analysis tools hosted on their own secure servers that connect to the data server via rsa key-pair authenticated ssh-tunneling on non-standard ports (e.g. ssh -L 54000:localhost:5432 for connection to a PostgreSQL server). For example, if a researcher is going to use the R statistical system to analyze the data records, the researcher will log into the RStudio Server. From RStudio Server, which has been granted limited access to file-based data sets and data records stored in a database, the researcher will run the required analyses. Results of the analyses can only be saved to the researchers home directory on the hosting server. Researchers are not permitted to save analysis results to their office workstations.

##Destruction
As required by specific data use agreements, completed project data can be either securely archived on encrypted VBI backup servers or destroyed. For data that is to be destroyed, the encrypted LVM partition on which the data is housed is first wiped using the Unix 'shred' utility, overwriting all partition data files three times with multiple patterns by default. After the data is overwritten, the encrypted LVM partition is then destroyed.
