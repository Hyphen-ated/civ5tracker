import os, sys, shutil, subprocess, py2exe
from distutils.core import setup

# Here is where you can set the name for the release zip file and for the install dir inside it.
version = "0.4-SNAPSHOT"
installName = 'civ5tracker-' + version

# target is where we assemble our final install. dist is where py2exe produces exes and their dependencies
if os.path.isdir('target/'):
    shutil.rmtree('target/')
installDir = 'target/' + installName + '/'

sys.argv.append('py2exe')
setup(
    options = {'py2exe': {'bundle_files': 3, 'compressed': True}},
    windows = [{'script': "tracker.py"}],
    zipfile = None,
)
shutil.copytree('dist/', installDir + "dist/")

setup(
    options = {'py2exe': {'bundle_files': 3, 'compressed': True}},
    windows = [{'script': "civ5_tracker_webserver.py"}],
    zipfile = None,
)
shutil.copytree('dist/', installDir + "server/")



shutil.copytree('output files reference/', installDir + 'output files/')


shutil.copy('shortcut.lnk', installDir + "Run Civ 5 Tracker.lnk")
shutil.copy('options.json', installDir)
shutil.copy('definitions-bnw.json', installDir)
shutil.copy('definitions-nqmod.json', installDir)
shutil.copy('LICENSE.txt', installDir)
shutil.copy('README.md', installDir + 'README.txt')
shutil.make_archive("target/" + installName, "zip", 'target', installName + "/")