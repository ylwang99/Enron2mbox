# About Dovecot

[Dovecot](http://www.dovecot.org/) is an open source IMAP and POP3 email server for Linux/UNIX-like systems. Here we'll show how to run Dovecot as an IMAP server on such systems and how to have local email clients connect to the server to view the data.

# Prepare Data (Enron Email Dataset)

1. Download this repo:
    ```
    $ git clone https://github.com/ylwang99/Enron2mbox.git
    ```

2. Download the [Enron Email Dataset](https://www.cs.cmu.edu/~./enron/) dataset, specifically, the [May 7, 2015 Version of dataset](https://www.cs.cmu.edu/~./enron/enron_mail_20150507.tgz). This dataset is distributed in [maildir](https://en.wikipedia.org/wiki/Maildir) format, which means that each message is stored in a separate file.

Here is how you can perform the download in the terminal:
    ```
    $ wget https://www.cs.cmu.edu/~./enron/enron_mail_20150507.tgz
    ```

3. Unpack the dataset:
    ```
    $ tar xvfz enron_mail_20150507.tgz
    ```
    This should give you a folder named `maildir`.

4. Move `maildir` to our project repo:
    ```
    $ mv maildir/ Enron2mbox/
    ```

5. Get into the repo and run the format script:
    ```
    $ cd Enron2mbox/
    $ ./format_enron.py
    ```
    This script: 
    * Mark all the emails as read (by appending each message filename with `:2,S`. For more details about the flags, refer [here](http://cr.yp.to/proto/maildir.html)).
    * Change the owner's access to the email collection to only lookup and read (by adding a `dovecot-acl` file into each folder. For more details about Dovecot Access Control Lists (ACL), refer [here](http://wiki2.dovecot.org/ACL)).
    
    Note that the script is destructive, in that it alters the original structure of the dataset. This is necessary to get everything in the right maildir format (in particular, the script creates cur/, new/ and tmp/ directories, which is part of the expected layout).

# Get Server to Run
### Install Dovecot

1. Install Dovecot:
    
    For Mac OS X:
    ```
    $ brew install dovecot
    ```
    For Fedora and RHEL (and CentOS/Scientific Linux/...):
    ```
    $ yum install dovecot
    ```
    
### Configure Dovecot

It's often the case that you want to have Dovecot behave in the way you want (eg. which port to listen to, where to find mails etc.), and it's the configure files (which shoud locate at `/etc/dovecot/` starting from `dovecot.conf`) we need to modify. 

1. File: `conf.d/10-mail.conf`:
    
    Comment out the line `#mail_location = ` and set the location to:
    ```
    mail_location = maildir:CHANGE_THIS_PATH:LAYOUT=fs
    ```
    Where `CHANGE_THIS_PATH` should point to the processed mail collection `maildir` (e.g., ~/maildir) in step 5 of section "Prepare Data".
    
2. File: `conf.d/90-acl.conf`:

    Change the lines that set Access Control Lists:
    ```
    plugin {
      #acl = vfile:/etc/dovecot/global-acls:cache_secs=300
    }
    ```
    to
    ```
    mail_plugins = acl
    plugin {
      acl = vfile
    }
    ```
    Here we specify to have an acl file for each mailbox folder.
    
    Note that we're not changing Dovecot authentication, and are using Dovecot's default authentication which is to use system user authentication. If you plan to use virtual users, refer [here](http://wiki2.dovecot.org/BasicConfiguration) and look for "Authentication".
    
### Running Dovecot

First make sure that port 143 is open for listening.

1. Start the server:
    ```
    $ dovecot
    ```
    If you make change to the config file, restart the server:
    ```
    $ doveadm reload
    ```

2. Stop the server:
    ```
    $ doveadm stop
    ```

# Get Email Client to Work
I've got a Amazon EC2 Linux instance to run, so you can skip the "Get Server to Run" section and directly start from here. And you get to behave as a system user when logging in.

### Apple Mail
1. In Apple Mail, open Mail->Preferences, select Accounts, click on "+" on the bottom left to add an account.

2. Select "Add Other Mail Account" in the pop-up window, then click "Continue".

3. Enter the information for the account, Full Name as you want, Email Address `ec2-user@35.162.97.62`, Password `dovecot`. Click "Create", then "Next" to manually configure.

4. Under IMAP, type `35.162.97.62` as Mail Server, `ec2-user` as User Name, `dovecot` as Password. Click "Next". "Connect" anyway if it warns you about some certificate issues.

5. For Outgoing Mail Server Info, type `35.162.97.62` as SMTP Server, leave User Name and Password empty because we're not using Apple Mail to send emails for this account, and just some toy data should be fine. Should it prompt to ask you for additional information about Outgoing Mail Server Info, just type something that's working.

6. Click "Create", and you should be able to see all the Enron emails as labeled emails for account `ec2-user@35.162.97.62` on the bottom left of Apple Mail. 

7. You're good to go!

### Thunderbird
1. In Thunderbird, go to the main page, and select "create a new email account".

2. Enter the information for the account, Full Name as you want, Email Address `ec2-user@35.162.97.62`, Password `dovecot`. Click "Continue", then "Manual config" to manually configure.

3. For Incoming, type `35.162.97.62` as Server hostname, select `143` as Port number.

4. For Outgoing, choose a working Server hostname (e.g., smtp.gmail.com). `35.162.97.62` is not working at the moment because it's not a SMTP server yet.

5. Click on "Re-test", and you should see the Button "Done" enabled. Click "Done". "Confirm Security Exception" if it warns you about some certificate issue. Now the account `ec2-user@35.162.97.62` should be displayed on the left panel.

6. Right click on account `ec2-user@35.162.97.62`, select "Subscribe...", and you get to choose what mailboxes you want to subscribe.

7. You're good to go!
