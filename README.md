# pyrotation
A numpy-based rotation library

[![Build Status](https://travis-ci.com/ChristofDubs/pyrotation.svg?branch=master)](https://travis-ci.com/ChristofDubs/pyrotation) [![Language grade: Python](https://img.shields.io/lgtm/grade/python/g/ChristofDubs/pyrotation.svg?logo=lgtm&logoWidth=18)](https://lgtm.com/projects/g/ChristofDubs/pyrotation/context:python) [![Coverage Status](https://coveralls.io/repos/github/ChristofDubs/pyrotation/badge.svg?branch=master)](https://coveralls.io/github/ChristofDubs/pyrotation?branch=master)

## Getting started

### Prerequisites

- Install [numpy](https://docs.scipy.org/doc/numpy-1.15.0/user/install.html)

### Installation

The recommended way is installing the package using pip:

```shell
pip install git+https://github.com/ChristofDubs/pyrotation.git@v0.0.1#egg=pyrotation
```

Alternatively, clone this repo:

```bash
git clone https://github.com/ChristofDubs/pyrotation.git
```

## Usage

Example:

```python
from pyrotation import quat_from_angle_axis, quat_from_roll_pitch_yaw
import numpy

q1 = quat_from_angle_axis(0.5, numpy.array([1,1,0]))
q2 = quat_from_roll_pitch_yaw(0.3, -0.8, 2.4)
q3 = q1.inverse() * q2
rot3 = q3.rotation_matrix()
```

To view all available functions, run `pydoc pyrotation` in the terminal, or type `import pyrotation` followed by `help(pyrotation)` in a python file.

## License

[![License](http://img.shields.io/:license-mit-blue.svg?style=flat-square)](http://badges.mit-license.org)