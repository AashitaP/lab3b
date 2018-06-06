# Create a symlink to lab3b
build: lab3b.py
	rm -rf lab3b
	ln -s lab3b.py lab3b
	chmod +x lab3b
	echo "symlink created"

# Deletes all makefile-created files
clean:
	rm -f lab3b *.tar.gz *~

# Build the distribution tarball
dist: 
	tar -cvzf lab3b-004810708.tar.gz lab3b.py Makefile README