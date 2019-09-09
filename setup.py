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
    version='1.3.0',
    author='Alex Coleman',
    author_email='a.coleman1@leeds.ac.uk',
    description='A toolkit for simulating UK crime data.',
    lisence='MIT LIcense',
    long_description=readme(),
    long_description_content_type='text/markdown',
    python_requires= '>=3.5',
    packages=find_packages(),
    #package_dir={'crime_sim_toolkit' : 'crime_sim_toolkit'},
    #package_data={
                # removed brackets on glob paths
                # added file types
                #'' : ['*.csv'],
                #'crime_sim_toolkit' : ['tests/testing_data/*.*']
    #},
    zip_safe=False,
    # removed as a test
    include_package_data=True


)
