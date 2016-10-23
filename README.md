# About Dovecot

Dovecot is an open source IMAP and POP3 email server for Linux/UNIX-like systems. Here we'll show how to have Dovecot run as a local IMAP server on Mac OS system.
# Install Dovecot

1. Get Dovecot from Git:

    ```
    $ git clone https://github.com/dovecot/core.git dovecot
    ```

2. If you have already installed [Homebrew](http://brew.sh/) in your computer, skip this step, otherwise run the following to install Homebrew:

    ```
    $ /usr/bin/ruby -e "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install)"
    ```
    
3. Install the following software/packages with Homebrew:
    ```
    $ brew install autoconf && brew install automake && \
    brew install libtool && brew install pkg-config && \
    brew install gettext && brew install pandoc && \
    brew install openssl
    ```

4. Find openssl's build variables:
    ```
   $ brew info openssl
    ```
    And you'll find in the last three lines LDFLAGS, CPPFLAGS paths. Write them down somewhere. In my case, it's 
    ```
    LDFLAGS:  -L/usr/local/opt/openssl/lib
    CPPFLAGS: -I/usr/local/opt/openssl/include
    PKG_CONFIG_PATH: /usr/local/opt/openssl/lib/pkgconfig
    ```
    
5. Compile Dovecot:
    ```
    $ ./autogen.sh
    $ CPPFLAGS="-I/usr/local/opt/opensslinclude" LDFLAGS="-L/usr/local/opt/openssl/lib" \
    ./configure --enable-maintainer-mode
    $ make
    $ sudo make install
    ```
    Here replace CPPFLAGS and LDFLAGS with what you've written down from step 4.

    For later updates, you can use:
    ```
    $ git pull
    $ make
    $ sudo make install
    ```

6. Install prebuilt binaries:
    ```
    $ brew install dovecot
    ```

    And you're done installing Dovecot.
    
# Configure Dovecot

It's often the case that you want to have Dovecot behave in the way you want (eg. which port to listen to, where to find mails etc.), and it's the configure files we need to modify. Thanks are given to Fredrik Jonsson for a good [post](https://xdeb.org/node/1607) about this.

1. Find where dovecot's binaries is located:
    ```
    $ brew info dovecot
    ```
    Look for the line that contains "Cellar", in my case, it's `/usr/local/Cellar/dovecot/2.2.25`.
    Default configuration files are then located in `/usr/local/Cellar/dovecot/2.2.25/share/doc/dovecot/example-config`
    
2. Copy over some default configuration files:
    ```
    $ sudo cp -r /usr/local/Cellar/dovecot/2.2.25/share/doc/dovecot/example-config/* /usr/local/etc/dovecot
    ```
    Note that this will make a copy of `dovecot.conf` and other files into `/usr/local/etc/dovecot` where Dovecot looks for configuration file `dovecot.conf` when start running. 
    
3. Add a `local.conf` file `/usr/local/etc/dovecot/local.conf` with all our own settings. `dovecot.conf` will include that file if it exists.

    Here we follow our settings for a local only IMAP server with system user authentication.
    
    Make sure to replace all instances of CHANGE_THIS with your own information.
    
    ```
    # A comma separated list of IPs or hosts where to listen in for connections. 
    # "*" listens in all IPv4 interfaces, "::" listens in all IPv6 interfaces.
    # If you want to specify non-default ports or anything more complex,
    # edit conf.d/master.conf.
    listen = 127.0.0.1

    # Protocols we want to be serving.
    protocols = imap

    # Location for users' mailboxes. The default is empty, which means that Dovecot
    # tries to find the mailboxes automatically. This won't work if the user
    # doesn't yet have any mail, so you should explicitly tell Dovecot the full
    # location.
    #
    # If you're using mbox, giving a path to the INBOX file (eg. /var/mail/%u)
    # isn't enough. You'll also need to tell Dovecot where the other mailboxes are
    # kept. This is called the "root mail directory", and it must be the first
    # path given in the mail_location setting.
    #
    # There are a few special variables you can use, eg.:
    #
    #   %u - username
    #   %n - user part in user@domain, same as %u if there's no domain
    #   %d - domain part in user@domain, empty if there's no domain
    #   %h - home directory
    #
    # Some examples:
    #
    #   mail_location = maildir:~/Maildir
    #   mail_location = mbox:~/mail:INBOX=/var/mail/%u
    #   mail_location = mbox:/var/mail/%d/%1n/%n:INDEX=/var/indexes/%d/%1n/%n
    #
    #
    mail_location = mbox:/CHANGE_THIS_to_the_path_where_you_want_to_store_the_mail/:INBOX=/var/mail/%u


    # System user and group used to access mails. If you use multiple, userdb
    # can override these by returning uid or gid fields. You can use either numbers
    # or names.
    mail_uid = CHANGE_THIS_to_your_short_user_name_or_uid
    mail_gid = admin

    # SSL/TLS support: yes, no, required.
    ssl = no

    # Login user is internally used by login processes. This is the most untrusted
    # user in Dovecot system. It shouldn't have access to anything at all.
    default_login_user = _dovenull

    # Internal user is used by unprivileged processes. It should be separate from
    # login user, so that login processes can't disturb other processes.
    default_internal_user = _dovecot

    # Setting limits.
    default_process_limit = 10
    default_client_limit = 50
    ```
Note that here we use mbox format emails. And mail collection (you'll get mail collection in the next section) should go to "/CHANGE_THIS_to_the_path_where_you_want_to_store_the_mail/".

4. Create PAM file `/etc/pam.d/dovecot` to use system user authentication for email account verification. Copy the following in file `/etc/pam.d/dovecot`:
    ```
    auth       required       pam_opendirectory.so try_first_pass
    account    required       pam_nologin.so
    account    required       pam_opendirectory.so
    password   required       pam_opendirectory.so
    ```

5. There are some changes needed to the default conf files as well.

* File: `/usr/local/etc/dovecot/conf.d/10-ssl.conf`
    
    Comment out the lines that tries to read the non existent SSL cert and key:
    ```
    #ssl_cert = </etc/ssl/certs/dovecot.pem
    #ssl_key = </etc/ssl/private/dovecot.pem
    ```
    
* File `/usr/local/etc/dovecot/conf.d/10-mail.conf`

    Uncomment the line that locks write permission:
    ```
    mbox_write_locks = dotlock fcntl
    ```
    
# Running Dovecot

1. Run the server:
    ```
    $ sudo brew services start dovecot
    ```
    If you make change to the config file, restart the server:
    ```
    $ sudo brew services restart dovecot
    ```

2. Stop the server:
    ```
    $ sudo brew services stop dovecot
    ```

# Converting the Enron Email Dataset to mbox Format

The [Enron Email Dataset](https://www.cs.cmu.edu/~./enron/) is distributed in [maildir](https://en.wikipedia.org/wiki/Maildir) format, which means that each message is stored in a separate file. This is unwieldy to work with. Here's how you can convert maildir into [mbox](https://en.wikipedia.org/wiki/Mbox), where all messages in a folder are stored in a single mbox file.

Go fetch the dataset and then unpack:

```
$ tar xvfz enron_mail_20150507.tgz
```

The dataset should unpack into a directory called `maildir`. Use the script `count_messages.sh` to gather an inventory of the messages in each folder:

```
$ ./count_messages.sh
```

Verify the total number of messages in the dataset:

```
$ ./count_messages.sh | cut -d' ' -f1 | awk '{s+=$1} END {print s}'
517401
```

Now run the conversion script:

```
$ ./convert_enron_to_mbox.py
```

It might take a bit, so go grab a cup of coffee...

Note that the script is destructive, in that it alters the original structure of the dataset. This is necessary to get everything in the right `maildir` format so that it can be processed by Python tools (in particular, the script creates `cur/` and `new/` directories, which is part of the expected layout).

After the script completes, the resulting mbox files are stored in the `enron/` directory:

```
$ ls enron | wc
    3311    3311   93804
```

The repo includes `ReadMbox.java`, a very simple Java program that uses the [JavaMail API](https://java.net/projects/javamail/pages/Home) to read the mbox files. The dependent jars are checked into the repo for convenience, so you can compile directly:

```
$ javac -cp lib/javax.mail-1.5.6.jar:lib/mbox.jar ReadMbox.java
```

You can now examine a particular mbox file:

```
$ java -cp .:lib/javax.mail-1.5.6.jar:lib/mbox.jar ReadMbox enron/enron.allen-p._sent_mail
```

The program prints out the subject line of each email.

To verify the integrity of the entire dataset in mbox format, run:

```
$ ./verify_mbox.sh > mbox.log &
```

Confirm that the number of messages is exactly the same:

```
$ grep "Number of messages" mbox.log | cut -d' ' -f4 | awk '{s+=$1} END {print s}'
517401
```

Point mail_location in file `/usr/local/etc/dovecot/local.conf` to the converted enron email collection.

# View Enron Email in Apple Mail
1. In Apple Mail, open Mail->Preferences, select Accounts, click on "+" on the bottom left to add an account.

2. Select "Add Other Mail Account" in the pop-up window, then click "Continue".

3. Enter the information for the account, Full Name as you want, Email Address (here please use system user as username, system_username@localhost for example), Password being system user password used for computer login. Click "Create", then "Next" to manually configure.

4. Under IMAP, type localhost as Mail Server, type system user name as User Name, Password being system user password used for computer login. Click "Next". "Continue" on without a secured password. Click "Next". 

5. For Incoming Mail Server Info, leave Path Prefix empty, SSL unchecked (Port left as 143), Authentication selected as "Password". Click "Next".

6. For Outgoing Mail Server Info, type localhost as SMTP Server, leave User Name and Password empty because we're not using Apple Mail to send emails for this account, just some toy data should be fine.

7. Click "Create", and you should be able to see all the Enron emails as labeled emails for account system_username@localhost on the bottom left of Apple Mail. 

8. You're good to go!