from setuptools import setup

__version__ = "0.1"


setup(
    name="hanja-tagger",
    version=__version__,
    license="MIT",
    description="Online Hanja tagger (powered by Hanjaro)",
    author="Kang Min Yoo",
    author_email="kaniblurous@gmail.com",
    url="https://github.com/kaniblu/hanja-tagger",
    packages=[
        "hanjatagger",
        "hanjatagger.compat2unified",
        "hanjatagger.zh2hans"
    ],
    include_package_data=True,
    install_requires=[
        "requests",
        "beautifulsoup4"
    ]
)
