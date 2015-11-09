# PDFExploder
[![Build Status](https://api.travis-ci.org/WasatchPhotonics/PDFExploder.png?branch=master)](http://travis-ci.org/WasatchPhotonics/PDFExploder) [![Coverage Status](https://coveralls.io/repos/WasatchPhotonics/PDFExploder/badge.svg?branch=master&service=github)](https://coveralls.io/github/WasatchPhotonics/PDFExploder?branch=master)

Web service to create thumbnail views of PDF documents

Display a responsive web form. With the pdf uploaded by the user,
generate a variety of exploded page view thumbnails like those shown
below. Store the pdf and thumbnail links forever with permanent links.
Live demo at http://waspho.com:8082

![PDFExploder screenshot](/resources/demo.gif "PDFExploder screenshot")


Getting Started
---------------

    Create a python virtual environment
    sudo dnf install freetype-devel
    sudo dnf install gcc
    sudo dnf install libjpeg-devel
    sudo dnf install zlib-devel
    sudo dnf install ImageMagick-devel

- cd _directory containing this file_

- $VENV/bin/python setup.py develop

- $VENV/bin/nosetests --cover-erase --with-coverage --cover-package=stickercode

- $VENV/bin/pserve config/development.ini

