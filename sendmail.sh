#!/bin/bash

# This is a bash script that simulates `sendmail` to use it
# alongside programs such as pybliotecario
# It can be linked to /usr/bin/sendmail
# ~# ln -s ${PWD}/sendmail.sh /usr/bin/sendmail
# and programs such as cron will use it to send emails

email_content=""
while IFS= read -r line; do
  email_content="${email_content}${line}\n"
done

# Substitute here the path to pybliotecario
pybliotecario "${email_content}"
