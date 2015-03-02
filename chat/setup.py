from setuptools import setup, find_packages

setup(
	name='pyelachat',
	version='0.4',
	description='Pyela Eternal-Lands chat client',
	url='http://pyela.googlecode.com/',
        author = 'Alex Collins, Vegar Storvann',
        author_email = 'vegar@storvann.net',
	packages=find_packages(),
	entry_points = {
		'gui_scripts': [
			'pyelachat = gui.chat:launch_gui'
		]
	}
)
