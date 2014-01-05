## manictime-couchdb-sync

This small script can be used to query the SQL CE database file produced by the great product ManicTime, and then send activities to a CouchDB server. Even if you do not use ManicTime or CouchDB, you may find this example useful for how to do bulk updates to CouchDB, query the ManicTime database, or compiling an IronPython script to EXE. It is possible to execute this script as a Python file, or just download a compiled EXE and run that.

##### Requirements

- IronPython
- python-couchdb

##### How to use

First, make sure you have met the requirements above. IronPython is needed for access to SQL CE (I kept getting Multi-Step errors with adodbapi on NVARCHAR columns, so switched to IronPython). You will also need to install python-couchdb.

Create a file in the same directory as mt_sync.py called 'default.cfg'. The file needs to look like this:

```
[CouchDB]
url: http://localhost:5984/
username: admin
password: password
database: what-database-to-use

[ManicTime]
location: C:\Users\username\Desktop\ManicTime\Data\ManicTime.sdf
```

Now you can simply run mt_sync.py using IronPython's interpreter, e.g. '"C:\Program Files (x86)\IronPython 2.7\ipy" mt_sync.py

##### How to compile to EXE

If you wish to compile this to an EXE, so you do not need to install IronPython (e.g on a work computer without admin rights...), then you can do the following:

Copy the Lib directory from the IronPython install (C:\Program Files (x86)\IronPython 2.7\Lib) into the same folder as mt_sync.py
Download and copy the couchdb folder from python-couchdb, and put it in the same folder as mt_sync.py

Run the following command:

"C:\Program Files (x86)\IronPython 2.7\ipy" "C:\Program Files (x86)\IronPython 2.7\Tools\Scripts\pyc.py" /main:mt_sync.py /target:exe

This will give you an EXE called mt_sync.py that you can run without IronPython installed. Just copy everything in the folder (Lib, couchdb, default.cfg, mt_sync.dll, and mt_sync.exe) and you're good to go.

##### Download and use a pre-compiled EXE

1) Go to Releases and download mt_sync.zip
2) Copy the mt_sync folder to somewhere, e.g. your ManicTime Data directory
3) Edit default.cfg with your details
4) Run mt_sync.exe - it will keep running and poll the database every 60 seconds (maybe to be 5 minutes in the future).