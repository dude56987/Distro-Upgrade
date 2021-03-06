#! /usr/bin/python
########################################################################
# Upgrades Ubuntu based distros by updating the sources for apt
# Copyright (C) 2014  Carl J Smith
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
########################################################################
import os, urllib2, sys
from time import sleep
########################################################################
# TODO:
#      * LTS ask if you want to stay on the LTS unless their is a new 
#        LTS release out to upgrade to then the upgrade informs the user
#        a new LTS it out and asks to upgrade to it
#      * Add a system in which the program pings all new repos to verify
#        they exist. Then if none of them work show error and dont 
#        preform the update. Also weigh the option of asking the user if
#        they would like to keep old repo versions if new ones dont work
#        , not on a wholistic basis but for each broken repo.
#      * Once a month set a cron job to check if a distro upgrade is 
#        available, if so notify the user using the same method as the
#        reboot-required program. Only tell them to run distro-upgrade.
#      * When program check distro and checks if mint can be updated it
#        will only work on the newest versions of the distros this
#        the program needs setup so that it will work with older 
#        versions too. 
#      * Add a --force -f option that skips the distro check stuff
#      * Add a --help option so the user can figure out how to use this
#        program.
#      * Clean up this pile of code so its not a hellhole of maintence 
#        in the future.
########################################################################
# ABOUT:
#       Program currently grabs Ubuntu, mint, and Debian distrowatch 
#       pages and figures out version names from them. Then upgrades the
#       package sources, and updates the system. If anything fails to 
#       download the program will end immediately since all data is 
#       needed and needs to be correct. OTHERWISE a massive fucking 
#       shitstorm will ensue.
########################################################################
#text formating command globals
resetTextStyle='\033[0m'
boldtext='\033[1m'
blinktext='\033[5m'
#textcolors
blacktext = '\033[30m'
redtext= '\033[31m'
greentext= '\033[32m'
yellowtext= '\033[33m'
bluetext= '\033[34m'
magentatext= '\033[35m'
cyantext= '\033[36m'
whitetext= '\033[37m'
#background colors
blackbackground= '\033[40m'
redbackground= '\033[41m'
greenbackground= '\033[42m'
yellowbackground= '\033[43m'
bluebackground= '\033[44m'
magentabackground= '\033[45m'
cyanbackground= '\033[46m'
whitebackground= '\033[47m'
########################################################################
def loadFile(fileName):
	try:
		fileObject=open(fileName,'r');
	except:
		print "Failed to load :",fileName
		return False
	fileText=''
	lineCount = 0
	for line in fileObject:
		if line[:1] != '#':
			fileText += line
		lineCount += 1
	fileObject.close()
	if fileText == None:
		return False
	else:
		return fileText
	#if somehow everything fails return false
	return False
class updateSources:
	def __init__(self,distrowatchPage):
		self.distroUrl = distrowatchPage
		# download the HTML webpage from Distrowatch to see the current versions available
		try:
			versions = urllib2.urlopen(distrowatchPage)
		except:# if page fails to load kill program it has failed
			print 'Distrowatch page failed to download...'
			raw_input('Press enter to end the program...')
			exit()
		temp = ''
		for line in versions:
			temp += line
		versions = temp
		temp = ''
		# search for the top of the table which displays the distro codenames
		# the codenames are used for the repos, this allows a sed replace in the repo sources
		start = versions.find('<table>\n  <tr>\n   <th class="TablesInvert">Feature</th>\n')
		# bottom looks like this
		end = versions.find('   <th class="TablesInvert">Feature</th>\n  </tr>\n')
		# rip the data out of the versions into an array
		versions = versions[(start+len('<table>\n  <tr>\n   <th class="TablesInvert">Feature</th>\n')):end]
		versions = versions.split('\n')
		# build that array
		for line in versions:
			temp += line.replace('    <td class="TablesInvert">','').replace('</td>','').replace(' LTS','')+'\n'
		# split back up the text file and build an array with it
		temp = temp.split('\n')
		versions = []
		for line in temp:
			# 2d array with each item in main array containing an array with
			# 2 data values, the version number and the codename
			versions.append(line.split('<br>'))
		# clean blank and snapshot versions
		temp = []
		for item in versions:
			if (item == ['']) or (item[0] == 'snapshot') or (item[0] == 'unstable') or (item[0] == 'testing'):
				#~ print 'Nope'
				pass
			else:
				temp.append(item)
				#~ print item
		# class variable
		self.versions = versions = temp
		temp = ''
		self.versions =list(reversed(self.versions))
		# add a number to each version
		temp = []
		counter = 0
		for item in self.versions:
			item.append(counter)
			temp.append(item)
			counter +=1
		self.versions = temp
		temp = ''
		# set and search for newest version
		self.newestVersion = self.versions[0]
		for item in self.versions:
			if item[0].find('rc') == -1: # dont count relese canadates
				if float(item[0]) > float(self.newestVersion[0]):
					self.newestVersion = item
		#print 'Newest version =',newestVersion
	def changeSources(self):
		for item in self.versions:
			os.system("sed -i.bak 's/"+item[1]+"/"+self.newestVersion[1]+"/g' /etc/apt/sources.list")
			os.system("sed -i.bak 's/"+item[1]+"/"+self.newestVersion[1]+"/g' /etc/apt/sources.list.d/*.list")
########################################################################
def updateSoftware(installCommand):
	# note that the dist-upgrade option is included to update the kernel automatically
	os.system(installCommand+' update --assume-yes')
	# the first command below fixes broken packages, if broken, otherwise it does nothing
	os.system(installCommand+' -f install')
	os.system(installCommand+' install --fix-missing')
	# the -o options in the below commands make them automatically update config files
	# changed in the updates if they have not been edited by hand
	os.system(installCommand+' -o Dpkg::Options::="--force-confdef" -o Dpkg::Options::="--force-confnew" upgrade --assume-yes')
	os.system(installCommand+' -o Dpkg::Options::="--force-confdef" -o Dpkg::Options::="--force-confnew" dist-upgrade --assume-yes')
	# here is a webpage on the above code http://raphaelhertzog.com/2010/09/21/debian-conffile-configuration-file-managed-by-dpkg/
	# this is because the -o options are kinda hard to remember
	os.system('echo "Removing unused packages..."')
	os.system(installCommand+' autoremove --assume-yes')
	os.system('echo "Clearing downloaded files..."')
	os.system(installCommand+' clean --assume-yes')
########################################################################
#check for root since shortcuts need to be installed for all users
if os.geteuid() != 0:
	print 'ERROR: this program must be ran as root!'
	print 'This program will upgrade the system for all users!'
	exit()
########################################################################
# what distro is this, load the files
sourcesText = ''
temp = loadFile('/etc/apt/sources.list')
if temp != False:
	sourcesText += temp
for files in os.listdir('/etc/apt/sources.list.d/'):
	temp = loadFile('/etc/apt/sources.list.d/'+files)
	if temp != False:
		sourcesText += temp
# check for mint then check for ubuntu, latter add other distros like zandros or something
# check for mint sources
distros = []
# linux mint sources
distros.append(updateSources('http://distrowatch.com/table.php?distribution=mint'))
# check for ubuntu sources
distros.append(updateSources('http://distrowatch.com/table.php?distribution=ubuntu'))
# debian sources
distros.append(updateSources('http://distrowatch.com/table.php?distribution=debian'))
# print the distros that will be updated
currentDistro = ''
if  sourcesText.find(distros[0].newestVersion[1]) != -1:
	print 'You are using Linux Mint'
	currentDistro = 'Linux Mint'
elif  sourcesText.find(distros[1].newestVersion[1]) != -1:
	print 'You are using Ubuntu Linux'
	currentDistro = 'Ubuntu Linux'
elif sourcesText.find(distros[2].newestVersion[1]) != -1:
	print 'You are using Debian Linux'
	currentDistro = 'Debian Linux'
# lists of versions of distros
if '-l' in sys.argv or '--list' in sys.argv:
	for item in distros:
		# if list is invoked list all distro versions and end the program
		print ('#'*6)+' '+(item.distroUrl.split('=')[1])+' '+('#'*6)
		for version in item.versions:
			print version[0]+' '+version[1]
	exit()
# check for mint if ubuntu versions and mint versions are compatable
if currentDistro == 'Linux Mint':
	if distros[1].newestVersion[2]-distros[0].newestVersion[2] != 1:
		print (redtext+'WARNING: Mint is currently not up to date with the current ubuntu packages, an upgrade now would break your system. Please wait until a new mint is out to upgrade.'+resetTextStyle)
		print 'Program will now exit...'
		exit()
print ('The following distro will be updated:')
print (greentext+currentDistro+resetTextStyle)
# query the user before the upgrade
print ('Would you like to upgrade the distro above?')
print (yellowtext+'NOTE: You should not make any changes to your computer while this is runnning!'+resetTextStyle)
if '-r' in sys.argv:# if reboot will happen at end up upgrade
	print (yellowtext+'NOTE: When the upgrade is complete your computer will reboot without warning!'+resetTextStyle)
print (yellowtext+'NOTE: A FRESH INSTALL IS ALWAYS BETTER THAN THIS METHOD!'+resetTextStyle)
print (redtext+'WARNING: MAKE SURE YOU\'VE BACKED STUFF UP, THIS COULD DESTROY THE SYSTEM!!!'+resetTextStyle)
# if force yes is used then skip question
if ('--force-yes' in sys.argv):
	temp = 'y'
else:
	temp = raw_input('[y/n]: ')
if temp == 'y':# if user answers yes proceed otherwise exit
	print ('Starting full distro upgrade,')
	print (redtext+'DO NOT SHUT DOWN DURING THIS PROCESS!'+resetTextStyle)
else:
	print 'Program will now exit, Nothing will be changed'
	exit()
if ('--force-yes' in sys.argv):
	countdown = 0
else:
	countdown = 30
for i in range(countdown):
	print (str(countdown-i) +' Seconds till the upgrade starts! Hit <CONTROL>+C to cancel!  ')
	sleep(1)
for item in distros:# do a sed search and replace for all the sources
	item.changeSources()
# figure out which package installer exists and prefer apt-fast
if os.path.exists('/usr/sbin/apt-fast'):
	installCommand = 'apt-fast'
elif os.path.exists('/usr/bin/apt-get'):
	installCommand = 'apt-get'
for index in range(10):
	# run update commands 10 times
	updateSoftware(installCommand)
if '-r' in sys.argv:
	os.system('reboot')
# if reboot dont work print below message on screen
print (greentext+boldtext+('#'*46)+resetTextStyle)
print (greentext+boldtext+('#'*46)+resetTextStyle)
print (bluetext+'UPGRADE COMPLETE! Please Reboot Your computer.'+resetTextStyle)
print (greentext+boldtext+('#'*46)+resetTextStyle)
print (greentext+boldtext+('#'*46)+resetTextStyle)
