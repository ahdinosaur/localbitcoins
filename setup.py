from setuptools import setup
setup(
    name = 'localbitcoins',
    version = "0.1dev",
    license = "GPL3",
    description = "trade bitcoins locally",
    long_description = open('README').read(),
    author = "dinosaur",
    author_email = "dinosaur@riseup.net",
    package_dir = { '' : 'src' },
    packages = [ 'localbitcoins'],
    install_requires = ['setuptools', 'requests'],
    entry_points = {
        'console_scripts' : [
            "main = localbitcoins.main:main",
            "test = localbitcoins.test.main:main"
            ]
        },
    zip_safe = False)
