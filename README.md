# SortableAssignment
Repo for Sortable Test

Hey there, 

Thanks again for your consideration!

I've tried to make this process as painless as possible, as I'm sure you've got better things to do then grade an assignment :)
My assignment has two primary dependencies, which you will need to install. I was able to get them directly from my RHEL7.2 repo, but your mileage may vary.

Requirements are:
Run as root
Internet access (for downloading updates/repos if required)
Python2 (tested version 2.7.5)
  Make sure your install includes python-pip and python-wheel as they are required to install the postgres driver
Postgres9.3 (include server and utils packages)
  If you use another version of python, you might need to muck around w/ the setup script since postgres includes their version numbers in their executables and I didn't code around that.
  
Otherwise, you should just be able to fire off the setup script, then run the application via python

python assignment.py y m d < input_file

I tried to make it run under other permissions, but with the setup it's kinda messy and I have a wedding to get to today so I couldn't fully debug it.

The application just uses the default 'postgres' database, and creates a user 'root' w/ password 'root'. If for some reason your setup runs into trouble. That's the big thing it requires.

If you need anything in terms of support to get it working. (you shouldn't) the robert carter help desk is open from 5pm-10pm weekdays and 10am-12pm weekends. Call toll free as long as you're in the 519 area code: 519-589-8860, we also accept texts or emails to robert.eg.carter@gmail.com.

I hope this meets your expectations, and I look forward to discussing my decisions w/ you.

Rob
