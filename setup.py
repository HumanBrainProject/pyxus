from setuptools import setup
from pip.req import parse_requirements

install_reqs = parse_requirements("requirements.txt", session=False)
reqs = [str(ir.req) for ir in install_reqs]

setup(
    name='pyxus',
    version='0.0.1',
    packages=['pyxus'],
    install_requires = reqs
)
