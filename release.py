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
setup(
    options = {'py2exe': {'bundle_files': 1, 'compressed': True}},
    windows = [{'script': "tracker.py"}],
    zipfile = None,
)


shutil.copytree('output files reference/', installDir + 'output files/')

shutil.copy('dist/tracker.exe', installDir)
shutil.copy('options.json', installDir)
shutil.copy('definitions-bnw.json', installDir)
shutil.copy('definitions-nqmod.json', installDir)
shutil.copy('LICENSE.txt', installDir)
shutil.copy('README.md', installDir + 'README.txt')
shutil.make_archive("target/" + installName, "zip", 'target', installName + "/")