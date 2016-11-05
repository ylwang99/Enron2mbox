#!/usr/bin/env python

import mailbox
import sys
import email
import os
import glob
import shutil

folders = []

file_subscription = open("maildir/subscriptions","a+")
# traverse root directory, and list directories as dirs and files as files
for root, dirs, files in os.walk("maildir"):
  if files or dirs:
    folder = root
    print("Processing " + folder)
    # change mailbox permission to lookup and read only (http://wiki2.dovecot.org/ACL)
    with open(folder + "/dovecot-acl","a+") as f:
      f.write("owner lr")
      f.close()
    if files:
      folder = root
      os.makedirs(folder + "/cur")
      os.makedirs(folder + "/new")
      os.makedirs(folder + "/tmp")
      for file in glob.glob(folder + "/[0-9]*."):
        # mark message read
        shutil.move(file, file + ":2,S")
        shutil.move(file + ":2,S", folder + "/cur")
      folder = root[8:]
      if len(folder) > 0:
      	file_subscription.write(folder + "\n")
file_subscription.close()


if os.path.exists("maildir/cur"):
  os.rmdir("maildir/cur")
if os.path.exists("maildir/new"):
  os.rmdir("maildir/new")
if os.path.exists("maildir/tmp"):
  os.rmdir("maildir/tmp")
if os.path.exists("maildir/dovecot-acl"):
  os.remove("maildir/dovecot-acl")