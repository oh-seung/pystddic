import setuptools

setuptools.setup(name='pystddic',
		version='0.0.4',
		description='Standard Dictionary Management(Korean Ver)',
		author='oh seung',
		author_email='seung.oh17@gmail.com',
		url='https://github.com/oh-seung/pystddic',
		python_requires='>=3.8',
		include_package_data=True,
		packages = setuptools.find_packages(),
		install_requires= ['pandas>=1.3', 
				   'numpy>=1.20',
				   'psutil>=5.8',
				   'ray>=1.12',
				   'tqdm>=4.62',
				  ]
    )
