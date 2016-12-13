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

If you don't have SSL settings in IMAP server and also want to use plain text authentication, do the following:

1. File: `conf.d/10-ssl.conf`:

    Change the line that uses ssl:
    ```
    ssl = required
    ```
    to
    ```
    ssl = no
    ```
    
2. File: `conf.d/10-auth.conf`:

    Change the line that doesn't allow plaintext authentication:
    ```
    disable_plaintext_auth = yes
    ```
    to
    ```
    disable_plaintext_auth = no
    ```
    
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

3. Enter the information for the account, Full Name as you want, Email Address `ec2-user@35.161.155.106`, Password `dovecot`. Click "Create", then "Next" to manually configure.

4. Under IMAP, type `35.161.155.106` as Mail Server, `ec2-user` as User Name, `dovecot` as Password. Click "Next". "Connect" anyway if it warns you about some certificate issues.

5. For Outgoing Mail Server Info, type `35.161.155.106` as SMTP Server, leave User Name and Password empty because we're not using Apple Mail to send emails for this account, and just some toy data should be fine. Should it prompt to ask you for additional information about Outgoing Mail Server Info, just type something that's working.

6. Click "Create", and you should be able to see all the Enron emails as labeled emails for account `ec2-user@35.161.155.106` on the bottom left of Apple Mail. 

7. You're good to go!

### Thunderbird

1. In Thunderbird, go to the main page, and select "create a new email account".

2. Enter the information for the account, Full Name as you want, Email Address `ec2-user@35.161.155.106`, Password `dovecot`. Click "Continue", then "Manual config" to manually configure.

3. For Incoming, type `35.161.155.106` as Server hostname, select `143` as Port number.

4. For Outgoing, choose a working Server hostname (e.g., smtp.gmail.com). `35.161.155.106` is not working at the moment because it's not a SMTP server yet.

5. Click on "Re-test", and you should see the Button "Done" enabled. Click "Done". "Confirm Security Exception" if it warns you about some certificate issue. Now the account `ec2-user@35.161.155.106` should be displayed on the left panel.

6. Right click on account `ec2-user@35.161.155.106`, select "Subscribe...", and you get to choose what mailboxes you want to subscribe.

7. You're good to go!

# Get Roundcube to Work on Local Systems

[Roundcube](https://roundcube.net/) is a browse-based multilingual IMAP client with an application-like user interface. It provides full functionality you expect from an email client. Hence, if you would like a browse-based IMAP client to connect to the email server, you can continue reading.

The following steps assume that you're getting Roundcube to run on a Mac/Windows/Amazon Linux system, for Ubuntu/Linux Mint, please refer [here](http://ubuntuportal.com/2012/02/an-easy-step-by-step-to-installing-and-running-roundcube-webmail-on-ubuntu-linux-mint.html).
    
To get Roundcube to work, we need to first set up our personal webserver, and the easiest way is to install the application MAMP (Macintosh, Apache, MySQL, and PHP) which allows you to have access to a local PHP server and MySQL server. Similar application for Linux is called LAMP.

### Install MAMP on Mac OS/Windows

I haven't tested on a Windows machine, but it should be similar to the following.

1. Go to [MAMP download page](https://www.mamp.info/en/downloads/) and download a version that's compatible with your OS. In my case, I downloaded MAMP & MAMP PRO 4.0.6 (Mac OS X). Althouth it comes with MAMP PRO which provides more functionality, we can actually ignore it since MAMP is enough for our use.

2. Install MAMP you have just downloaded, then just follow the instructions which should be fairly easy.

3. Open and launch MAMP. 

4. To configure the server, go to `Preferences...`.
    * Select `Ports`, you can choose to use default ports (Apache 8888 for example, in this case, you'll need to type localhost:8888 to open your personal webpage) or set Web port to 80 so you don't have to type a port number after localhost when you open your personal webpage. If you set the Web port to 80, make sure to run `sudo apachectl stop` to stop Mac's own Apache server. In my case, I set the Web port to 80 for simplicity.

5. Click on `Start Servers` if the Apache and MySQL servers haven't shown on the top right to be started.

6. To create a MySQL Database & User, click on `Open WebStart Page`, under `Tools`, click on `phpMyAdmin`. Under `Databases`, create a database called `roundcubedb`, and it will show on the left panel. Click on this database, under `Privileges`, add a new user account `usercube` with password `usercube`, grant it all privileges by checking all Global privileges. Finally click `Go`. 

### Install Roundcube

1. Go to the [Roundcube donwload page](https://roundcube.net/download/) and download a Complete version. In my case, I downloaded `roundcubemail-1.2.3-complete.tar.gz`. All the following steps assume the same file, and you can change according to what file you download.

2. Unpack the file:
    ```
    $ tar xvfz roundcubemail-1.2.3-complete.tar.gz
    ```
    
3. Rename the extracted folder to `webmail` (just for easiness):
    ```
    $ mv roundcubemail-1.2.3 webmail
    ```

4. In MAMP, go to `Preferences...`, select `Web Server`, from where you should see `Document Root`, move the `webmail` folder under this `Document Root`.
    
5. To configure Roundcube, in a browser, open `http://localhost/webmail/installer`.
    * Under `Check environment` you should see several OKs except for a few NOT AVAILABLE which we don't actually care. If there's any NOT OK, please fix it before you can click on `NEXT`.
    * Under `Create config`, type `roundcubedb` as the Database server, `usercube` as the Database user name and `usercube` as the Database password, `35.161.155.106` as the IMAP host server, `143` as the default_port, `en_US` as the language. Finally, click on `CREATE CONFIG`.
    * Under `Test config`, you should see all OKs except for a NOT OK for DB Schema, click on 'Initialize databse' to fix it. Type `ec2-user` as Username and `dovecot` as Password for Testing IMAP config, click on `Check login`, and you should be able to see a successful message "IMAP connect:  OK". Fix any problem you might have before proceeding to the next step.

6. You should now be able to connect to the mail server using Roundcube by going to `http://localhost/webmail/` with username `ec2-user` and password `doveoct`.

7. Finally, go to your `webmail` folder and delete the `installer` folder.

# Get Roundcube to Work on Amazon Linux

I mostly followed [here](http://docs.aws.amazon.com/AWSEC2/latest/UserGuide/install-LAMP.html) for setting up the servesr and [here](http://ubuntuportal.com/2012/02/an-easy-step-by-step-to-installing-and-running-roundcube-webmail-on-ubuntu-linux-mint.html) for creating the databse & user. The steps are quite similar to that of Mac OS/Windows above.

If you want to skip all the troublesome, I've set up the Roundcube on a Amazon Linux you can play with: `54.226.216.31/webmail/` with username `ec2-user` and password `dovecot`.

### Install LAMP

1. Connect to your instance, make sure that your instance has the port 80 (HTTP) open (by modifying the security group this instance is bounded to).

2. Make sure the software packages are up to date:
	```
    $ sudo yum update -y
    ```
3. Install the Apache web server, MySQL, and PHP software packages:
    ```
    $ sudo yum install -y httpd24 php56 mysql55-server php56-mysqlnd php56-mbstring
    ```
4. Start the Apache web server:
    ```
    $ sudo service httpd start
    ```
    To test your web server, in a web browser, enter the public DNS address (or the public IP address) of your instance, you should see the Apache test page.

5. Start the MySQL server:
    ```
    $ sudo service mysqld start
    ```

6. Run mysql_secure_installation to set a password for the root user:
    ```
    $ sudo mysql_secure_installation
    ```
    * When prompted, it asks to enter a password for the root account. Because by default, the root account does not have a password set, so press Enter.

    * Type Y to set a password, and enter a secure password twice.

    * Type Y to remove the anonymous user accounts.

    * Type Y to disable remote root login.

    * Type Y to remove the test database.

    * Type Y to reload the privilege tables and save your changes.
    
7. To create a MySQL Database & User:
    * Open the terminal and run the following command to log in to MySQL server (use the MySQL password you have entered during the installation of the LAMP Server):
	```
	$ mysql -u root -p
	```
    * Create a database for Roundcube Webmail, for example: `roundcubedb`
	```
	mysql> create database roundcubedb;
	```
    * Create MySQL user for access  Roundcube Webmail, for example: `usercube`
	```
	mysql> create user usercube;
	```
    * Give user `usercube` a password `usercube`:
	```
	mysql> set password for 'usercube' = password('usercube');
	```
    * Set  privileges usercube to access database roundcubedb:
	```
	mysql> grant all privileges on roundcubedb.* to 'usercube' identified by 'usercube';
	```
    * Exit from MySQL:
	```
	mysql> exit
	```
   
### Install Roundcube

1. Go to the [Roundcube donwload page](https://roundcube.net/download/) and download a Complete version. In my case, I downloaded `roundcubemail-1.2.3-complete.tar.gz`. All the following steps assume the same file, and you can change according to what file you download.

2. Unpack the file:
    ```
    $ tar xvfz roundcubemail-1.2.3-complete.tar.gz
    ```
    
3. Rename the extracted folder to `webmail` (just for easiness):
    ```
    $ mv roundcubemail-1.2.3 webmail
    ```
   
4. Because the Amazon Linux Apache document root is `/var/www/html`, so let's move `webmail` to `/var/www/html`

5. To configure Roundcube, in a browser, open `http://my.public.dns.amazonaws.com/webmail/installer`.
    * Under `Check environment` you should see several OKs except for a few NOT AVAILABLE which we don't actually care. You might see `date.timezone:  NOT OK(not set)`, to fix it, open file `php.ini` (you can find it by doing this: first create a simple PHP file `/var/www/html/phpinfo.php` with content `<?php phpinfo(); ?>` using `sudo vim`. In a browser, open `http://my.public.dns.amazonaws.com/phpinfo.php`, `php.ini` is then labeled as `Loaded Configuration File`), locate `;date.timezone =` and change it to `date.timezone = "US/Eastern"`. Restart Apache and MySQL servers by running `sudo service httpd restart;sudo service mysqld restart` and then reload `http://my.public.dns.amazonaws.com/webmail/installer`. If there's still any other NOT OK, please fix it before you can click on `NEXT`.
    * Under `Create config`, type `roundcubedb` as the Database server, `usercube` as the Database user name and `usercube` as the Database password, `35.161.155.106` as the IMAP host server, `143` as the default_port, `en_US` as the language. Finally, click on `CREATE CONFIG`, it should show the content of the config file, copy and save it as file `config.inc.php` within the `/var/www/html/webmail/config/` directory.
    * Under `Test config`, you should see all OKs except for two NOT OKs for directories not writable and one NOT OK for DB Schema. For the first two, run `sudo chown -R apache.apache /var/www/html/webmail/temp/` and `sudo chown -R apache.apache /var/www/html/webmail/logs/`, then refresh the page. For the second one, click on 'Initialize databse' to fix it. Type `ec2-user` as Username and `dovecot` as Password for Testing IMAP config, click on `Check login`, and you should be able to see a successful message "IMAP connect:  OK". Fix any problem you might have before proceeding to the next step.

6. You should now be able to connect to the mail server using Roundcube by going to `http://my.public.dns.amazonaws.com/webmail/` with username `ec2-user` and password `doveoct`.

7. Finally, go to your `webmail` folder and delete the `installer` folder.

# Play ePADD with Enron collection

[ePADD](http://epadd.stanford.edu/epadd/collections) is a platform that allows researchers to browse and search historical email archives. ePADD can be run on 64-bit, Windows 7 SP1/10, Mac OS X 10.11/10.12.

### Install ePADD on Windows

1. Please download the latest ePADD distribution files (.exe) from `https://github.com/ePADD/epadd/releases/`. You will need to have Java 8 or later installed on your machine for ePADD to work properly.

2. When you run ePADD for the first time, a directory for the Appraisal Module is created to store working files. When ePADD starts up, it checks this directory and relies upon it to resume earlier work. If the software does not locate this directory, ePADD will create it. The ePADD Appraisal Module directory is located at c:\users\<username>\epadd-appraisal. 

3. In order for functionality for authority reconciliation to function correctly, you must also separately download the configuration files (epadd-settings.zip), accessible via https://github.com/ePADD/epadd/releases/. Once downloaded, unzip this file into your user directory (c:\users\<username>\).

###  Installing ePADD on OSX

1. Please download the latest ePADD distribution files (.dmg) from https://github.com/ePADD/epadd/releases/. You will need to have Java 8 or later installed on your machine for ePADD to work properly.

2. When you run ePADD for the first time, a directory for the Appraisal Module is created to store working files. When ePADD starts up, it checks this directory and relies upon it to resume earlier work. If the software does not locate this directory, ePADD will create it. The ePADD Appraisal Module directory is located at Macintosh HD/Users/<username>/epadd-appraisal.

3. In order for functionality for authority reconciliation to function correctly, you must also separately download the configuration files (epadd-settings.zip), accessible via  https://github.com/ePADD/epadd/releases/. Once downloaded, unzip this file into your user directory (Macintosh HD/Users/<username>/). 

### Convert Maildir Enron collection to Mbox format

Run the conversion script:
```
./convert_enron_to_mbox.py
```
It might take a bit, so go grab a cup of coffee...

Note that the script is destructive, in that it alters the original structure of the dataset.

### Import Mbox email collection to ePADD

1. Open the application ePADD you've downloaded from above, which opens a webpage for you.

2. On the page, click on `Import` on the top left.

3. You can actually choose to import from public email accounts or private email accounts by specifying the IMAP Server. But here we choose to import directly from Mbox file. So browse the folder you want to import (I suggest you import one folder/inbox at a time because processing takes time), give it a email source name, click on `Continue`. 

4. All the following steps should be straightforward, and you can do all the processes by following the well-written [instructions](https://docs.google.com/document/d/1joUmI8yZEOnFzuWaVN1A5gAEA8UawC-UnKycdcuG5Xc/edit).
