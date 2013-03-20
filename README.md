hrva-wiki
=========

HRVA's LocalWiki

NOTE: This guide assumes that you have an S3 account with a bucket called `localwiki` where your backups will be stored.

## Standup New Instance with Backup on S3
1. Create an Amazon EC2 key pair and download it.
2. Create a new Amazon EC2 micro instance of Ubuntu 12.04 using the key pair.
3. Make sure that the Security Group being used for the instance has inbound port 80 opened.
4. SSH into the instance

   ```
   $ ssh -i KEY_PAIR.pem ubuntu@INSTANCE_DNS
   ```

5. Install LocalWiki

   ```
   $ sudo apt-get install python-software-properties
   $ sudo apt-add-repository ppa:localwiki
   $ sudo apt-get update
   $ sudo apt-get install localwiki
   ```
   
6. Install and configure S3 Tools

   ```
   $ sudo apt-get install s3cmd
   $ s3cmd --configure
   ```
   
7. Copy the backup script

   ```
   #!/bin/bash

   timestamp=`date -u +%Y-%m-%d_%H-%M-%S`
   filename=localwiki-backup-$timestamp
   tempdir=~/backups/localwiki-backup-$timestamp

   # set stage
   mkdir $tempdir -p # make (-p) parent directories as needed

   # do the dirty work
   cp -r /usr/share/localwiki/ $tempdir/usr.share.localwiki/
   sudo -u postgres pg_dump -U postgres localwiki > $tempdir/localwiki.sql
   cp -r /etc/apache2/sites-enabled/ $tempdir/etc.apache2.sites-enabled # change to sites-available if you use standard symlinks

   # wrap it up
   tar -zcf $tempdir.tar.gz $tempdir
   # ignore issue "tar: Removing leading `/' from member names"
   # we don't need absolute file names (with -P), more info:
   # http://www.gnu.org/software/tar/manual/html_chapter/Choosing.html#SEC118

   # clean
   rm -rf $tempdir

   s3cmd put $tempdir.tar.gz s3://localwiki/$filename.tar.gz
   ```

8. Write the backup script to the server

   ```
   $ vi ~/backup.sh
   i
   [Ctrl-v]
   [Esc]
   :wq[Enter]
   $ chmod +x ~/backup.sh 
   ```

9. Get the backup to restore from S3

   ```
   $ s3cmd get s3://localwiki/BACKUP_FILE ~/BACKUP_FILE
   ```
   
10. Get database password from /usr/share/localwiki/conf/localsettings.py
11. Restore the backup

   ```
   $ cd ~
   $ tar -xzvf BACKUP_FILE
   $ cd EXTRACT_BACKUP_DIR
   $ sudo -u postgres psql
   DROP DATABASE localwiki;
   \q
   $ sudo -u postgres createdb -T template_postgis localwiki
   $ sudo -u postgres psql
   ALTER USER localwiki WITH PASSWORD '<database-password>';
   \q
   $ sudo -u postgres psql localwiki < localwiki.sql
   $ sudo rm -rf /usr/share/localwiki
   $ sudo cp -R usr.share.localwiki /usr/share/localwiki
   ```
   
TODO: Create script that schedules daily backups
