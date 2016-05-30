REM full path to the python interpretor
@set PYTHON=D:\Zope-2.7.2-0\bin\python.exe

REM path to ZOPE_HOME/lib/python
@set SOFTWARE_HOME=D:\Zope-2.7.2-0\lib\python

REM path to your instance. Don't set it if you aren't having  instance
@set INSTANCE_HOME=D:\MailArchive\zope_272

"%PYTHON%" run_tests.py