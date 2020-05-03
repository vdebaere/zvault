from setuptools import setup, find_packages

setup(
    name='zvault',
    version='0.1.0',
    description='Manage vaults backed by encrypted ZFS datasets',

    # The argparse module is new in 3.2
    # The typing module is new in 3.5
    python_requires='>=3.5',

    packages=find_packages(),

    entry_points={
        'console_scripts': [
            'zvault = zvault.main:main'
        ]
    }
)
