show:
	echo 'Run "make install" as root to install program!'
	
run:
	python distro-upgrade.py
install:
	sudo apt-get install transmission-gtk --assume-yes
	sudo cp distro-upgrade.py /usr/bin/distro-upgrade
	sudo chmod +x /usr/bin/distro-upgrade
	sudo link /usr/bin/distro-upgrade /etc/cron.monthly/distro-upgrade
uninstall:
	sudo rm /usr/bin/distro-upgrade
	sudo rm /etc/cron.monthly/distro-upgrade
build: 
	sudo make build-deb;
build-deb:
	mkdir -p debian;
	mkdir -p debian/DEBIAN;
	mkdir -p debian/usr;
	mkdir -p debian/usr/bin;
	mkdir -p debian/usr/share;
	mkdir -p debian/usr/share/applications;
	# copy over the launcher for the menu, this will show up in the 
	# xfce settings manager
	cp -vf Distro-Upgrade.desktop ./debian/usr/share/applications/
	# make post and pre install scripts have the correct permissions
	chmod 775 debdata/*
	# copy over the binary
	cp -vf distro-upgrade.py ./debian/usr/bin/distro-upgrade
	# make the program executable
	chmod +x ./debian/usr/bin/distro-upgrade
	# start the md5sums file
	md5sum ./debian/usr/bin/distro-upgrade > ./debian/DEBIAN/md5sums
	md5sum ./debian/usr/share/applications/Distro-Upgrade.desktop >> ./debian/DEBIAN/md5sums
	# create md5 sums for all the config files transfered over
	sed -i.bak 's/\.\/debian\///g' ./debian/DEBIAN/md5sums
	rm -v ./debian/DEBIAN/md5sums.bak
	cp -rv debdata/. debian/DEBIAN/
	chmod -Rv go+r debian/
	dpkg-deb --build debian
	cp -v debian.deb distro-upgrade_UNSTABLE.deb
	rm -v debian.deb
	rm -rv debian
