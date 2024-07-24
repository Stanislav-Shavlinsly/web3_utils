from setuptools import setup, find_packages

setup(
    name='web3_utils',
    version='0.2.20',
    author='Stanislav Shavlinsky',
    author_email='stanislave777@gmail.com',
    description='Набор утилит для работы с Web3',
    long_description=open('README.md', encoding='utf-8').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/Stanislav-Shavlinsly/web3_utils',
    packages=find_packages(),
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.10',
    install_requires=[
        'attrs==23.2.0',
        'base58==2.1.1',
        'bitarray==2.9.2',
        'certifi==2024.2.2',
        'charset-normalizer==3.3.2',
        'colorama==0.4.6',
        'cytoolz==0.12.3',
        'eth-abi==2.2.0',
        'eth-account==0.5.9',
        'eth-hash==0.7.0',
        'eth-keyfile==0.5.1',
        'eth-keys==0.3.4',
        'eth-rlp==0.2.1',
        'eth-typing==2.3.0',
        'eth-utils==1.9.5',
        'hexbytes==0.3.1',
        'idna==3.6',
        'ipfshttpclient==0.7.0',
        'jsonschema==3.2.0',
        'lru-dict==1.3.0',
        'multiaddr==0.0.9',
        'netaddr==1.2.1',
        'parsimonious==0.8.1',
        'protobuf==3.20.3',
        'pycryptodome==3.20.0',
        'pyrsistent==0.20.0',
        'requests==2.31.0',
        'rlp==2.0.1',
        'six==1.16.0',
        'toolz==0.12.1',
        'urllib3==2.2.1',
        'varint==1.0.2',
        'web3==5.9.0',
        'websockets==8.1'
    ],
    entry_points={
        # Ваши консольные скрипты или точки входа
    },
    include_package_data=True,
    package_data={
        # Опционально: включаемые данные пакета
    },
    # Другие параметры...
)
