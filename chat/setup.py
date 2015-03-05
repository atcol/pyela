from setuptools import setup, find_packages
from gui import VER_MINOR,VER_MAJOR,VER_EXTRA

setup(
	name='pyelachat',
	version='{}.{}{}'.format(VER_MINOR,VER_MAJOR,VER_EXTRA),
	description='Pyela Eternal-Lands chat client',
	url='http://github.com/atc-/pyela',
        author = 'Alex Collins, Vegar Storvann',
        author_email = 'vegar@storvann.net',
	packages=find_packages(),
	entry_points = {
		'gui_scripts': [
			'pyelachat = gui.chat:launch_gui'
		]
	}
)
