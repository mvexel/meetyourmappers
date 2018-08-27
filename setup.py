from setuptools import setup

setup(
    name='meetyourmappers',
    version='0.1',
    description='Meet Your Mappers - Find OpenStreetMap Contributors Near You',
    author='Martijn van Exel',
    author_email='mym@rtijn.org',
    packages=['meetyourmappers'],
    include_package_data=True,
    install_requires=[
        'flask',
        'requests',
        'osmium'
    ],
)
