from setuptools import setup, find_packages

def readme():
    with open('README.md') as f:
        return f.read()

def read_reqs():
    with open('requirements.txt') as f:
        return [pkg.rstrip('\n') for pkg in f]

setup(
    name='crime_sim_toolkit',
    url='https://github.com/Sparrow0hawk/crime_sim_toolkit',
    version=1.2,
    author='Alex Coleman',
    author_email='a.coleman1@leeds.ac.uk',
    description='A toolkit for simulating UK crime data.',
    long_description=readme(),
    long_description_content_type='text/markdown',
    python_requires= '>=3.5',
    # changed to name of package
    packages=['crime_sim_toolkit'],
    package_data={
                # removed brackets on glob paths
                # added file types
                'crime_sim_toolkit' : 'src/LSOA_data/*.csv',
                'crime_sim_toolkit' : 'tests/testing_data/*.*'
    }
    # removed as a test
    #include_package_data=True


)
