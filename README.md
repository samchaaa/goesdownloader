goesdownloader
==============

[![Gitter](https://badges.gitter.im/Join%20Chat.svg)](https://gitter.im/gersolar/goesdownloader?utm_source=badge&utm_medium=badge&utm_campaign=pr-badge&utm_content=badge)

[![License](https://img.shields.io/pypi/l/goesdownloader.svg)](https://raw.githubusercontent.com/gersolar/goesdownloader/master/LICENSE) [![Downloads](https://img.shields.io/pypi/dm/goesdownloader.svg)](https://pypi.python.org/pypi/goesdownloader/) [![Build Status](https://travis-ci.org/gersolar/goesdownloader.svg?branch=master)](https://travis-ci.org/gersolar/goesdownloader) [![Coverage Status](https://coveralls.io/repos/gersolar/goesdownloader/badge.png)](https://coveralls.io/r/gersolar/goesdownloader) [![Code Health](https://landscape.io/github/gersolar/goesdownloader/master/landscape.png)](https://landscape.io/github/gersolar/goesdownloader/master) [![PyPI version](https://badge.fury.io/py/goesdownloader.svg)](http://badge.fury.io/py/goesdownloader)
[![Stories in Ready](https://badge.waffle.io/gersolar/goesdownloader.png?label=ready&title=Ready)](https://waffle.io/gersolar/goesdownloader)

A python library that made simple the download of images from a NOAA Class Suscription.

Requirements
============

If you want to use this library on any GNU/Linux or OSX system you just need to execute:

    $ pip install goesdownloader

If you want to improve this library, you should download the [github repository](https://github.com/gersolar/goesdownloader) and execute:

    $ make virtualenv deploy

On Ubuntu Desktop there are some other libraries not installed by default (zlibc curl libssl1.0.0 libbz2-dev libxslt-dev libxml-dev) which may need to be installed to use these library. Use the next command to automate the installation of the additional C libraries:

    $ make ubuntu virtualenv deploy


Testing
=======

To test all the project you should use the command:

    $ make test

If you want to help us or report an issue join to us through the [GitHub issue tracker](https://github.com/gersolar/goesdownloader/issues).


Example
=======

To download the recent images, the **download** method accepts 5 parameters:

```python
    from goesdownloader import instrument as goes 

    should_download = lambda dt: dt.hour - 4 >= 5 and dt.hour - 4 <= 20
    downloaded = instrument.download('user', 'password', 'directory',
                                     suscription_id='55253',
                                     datetime_filter=should_download)
```


About
=====

This software is developed by [GERSolar](http://www.gersol.unlu.edu.ar/). You can contact us to [gersolar.dev@gmail.com](mailto:gersolar.dev@gmail.com).
