import os, sys, shutil, subprocess, py2exe
from distutils.core import setup

# Here is where you can set the name for the release zip file and for the install dir inside it.
version = "0.1"
installName = 'civ5tracker-' + version

# target is where we assemble our final install. dist is where py2exe produces exes and their dependencies
if os.path.isdir('target/'):
    shutil.rmtree('target/')
installDir = 'target/' + installName + '/'

# then build the option builder using normal py2exe
sys.argv.append('py2exe')
setup(windows=['tracker.pyw'])

shutil.copytree('dist/', installDir)
shutil.copytree('output files reference/', installDir + 'output files/')

shutil.copy('options.json', installDir)
shutil.copy('definitions-bnw.json', installDir)
shutil.copy('definitions-nqmod.json', installDir)
shutil.copy('LICENSE.txt', installDir)
shutil.copy('README.md', installDir + 'README.txt')
with open(installDir + "version.txt", 'w') as f:
    f.write(version)
shutil.make_archive("target/" + installName, "zip", 'target', installName + "/")