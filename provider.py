#!/root/virtualenv/pychef/bin/python
import os
import sys
import shutil
import chef
from datetime import datetime, date
import time
import filecmp
from xml.sax.handler import ContentHandler
from xml.sax import make_parser
from glob import glob

# edit me
tmp = "/tmp/cache.xml"
destination = "/data/nginx/html/cache.xml"
log = "/var/log/chef/provider.log"
debug = False
# em tide

logdate = datetime.now().isoformat()
five_minutes_ago = time.time() - 300
timenow = time.strftime("%Y%m%d%H%M%S")

api = chef.autoconfigure()

def bugme(msg):
        if debug == True:
                print "DEBUG: %s" % msg

def logerror(msg):
	try: 
		l = open(log, 'a')
		fmsg = "ERROR: %s" % (msg)
		bugme(fmsg)
		l.write("%s %s\n" % (logdate, fmsg))
		l.close()
		if os.path.isfile(tmp):
			os.unlink(tmp)
		sys.exit()
	except:
		print "ERROR: unable to write to log file!"
		if os.path.isfile(tmp):
			os.unlink(tmp)
		sys.exit()

def testxml(file):
	try:
		parser = make_parser()
    		parser.setContentHandler(ContentHandler())
    		parser.parse(file)
		bugme("xml passed validation!")
        	return True
    	except Exception, e:
		return False


if os.path.isfile(tmp):
	st=os.stat(tmp)
	mtime=st.st_mtime
	if mtime < five_minutes_ago:
		logerror("%s older that 5 mintues, removing" % tmp)
    	else:
		logerror("%s exists. Assuming I'm already running and aborting!" % tmp)

try:
	f = open(tmp,'w')
	try:
		f.write("<project>\n")
	except:
		logerror("failed to open project tag")
	for node in chef.Node.list():
		n = chef.Node(node)
		bugme("processing: %s" %  node)
		tags = ""
		for r in n['roles']:
			tags += "%s," % r
			bugme("adding role %s to tags." % r)
		for t in n['tags']:
			tags += "%s," % t
			bugme("adding tag %s to tags." % t)
		tags = tags + n.chef_environment
		try:
			f.write('<node name="%s" type="Node" description="%s" osArch="%s" osFamily="unix" osName="%s" osVersion="%s" tags="%s" username="rundeck" hostname="%s" editUrl="http://chef.vast.com:4040/nodes/%s/edit"/>\n' % (n['fqdn'], n['fqdn'], n['kernel']['machine'], n['platform'], n['platform_version'], tags, n['fqdn'], node))
		except:
			logerror("failed to write entry for %s!" % n['fqdn'])
	try:
		f.write("</project>\n")
	except:
		logerror("failed to close project!")
	try:
		f.close()
	except:
		logerror("failed to close file!")
except:
	logerror("unable to generate new provider file!")

if testxml(tmp) == False:
	logerror("temporary xml wasn't valid! Cleaning up and aborting!")

bugme("new provider tmp generated: %s" % tmp)

if os.path.isfile(destination):
	if filecmp.cmp(destination, tmp) is False:
		rewrite = True
		backup = "%s-%s" % (destination, str(timenow))
		bugme("backing up to: %s" % backup)
		shutil.copy(destination, backup)
	else:
		rewrite = False
else:
		rewrite = True

if rewrite == True:
	try:
		shutil.move(tmp, destination)
		bugme("It worked!")
	except:
		logerror("issue moving %s to %s!" % (tmp, destination))
else:
	bugme("%s will not overwrite %s. All done." % (tmp, destination))
	os.unlink(tmp)
