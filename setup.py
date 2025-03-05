from setuptools import setup

setup(
    name="clipkeep",
    version="1.0",
    py_modules=["clipkeep"],
    install_requires=[
        "requests",
        "pyperclip",
        "python-socketio"
    ],
    entry_points={
        "console_scripts": [
            "clipkeep=clipkeep:main"
        ]
    }
)
