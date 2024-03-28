# MinMod Dashboard

<div align="center">

![Python](https://img.shields.io/badge/python-v3.8+-blue.svg)
[![GitHub Issues](https://img.shields.io/github/issues/usc-isi-i2/minmod-webapp.svg)](https://github.com/usc-isi-i2/minmod-webapp/issues)
[![Docker](https://img.shields.io/docker/automated/jrottenberg/ffmpeg.svg?maxAge=2592000)]()
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](https://github.com/usc-isi-i2/minmod-webapp/blob/main/LICENSE)
![Contributions welcome](https://img.shields.io/badge/contributions-welcome-orange.svg)

</div>

## Table of Contents

- [Introduction](#introduction)
- [Installation](#installation)

## Introduction

```
To Do.

```

<!-- For more documentation, please see [not available yet](). -->

## Installation

Install from pip: `pip install -r requirements.txt`

## Usage

Install [docker](https://docs.docker.com/engine/installation/) and run:

```shell
docker build -t dash-app .
docker run -p 8050:8050 dash-app
```

Otherwise, for the standalone web service:

```shell
pip install -r requirements.txt
python app.py
```

Visit [http://localhost:8050](http://localhost:5000)

## Development

Create a new branch off the **develop** branch for features or fixes.

After making changes rebuild images and run the app:

```shell
docker build -t dash-app .
docker run -p 8050:8050 dash-app
```

## Tests

```
To Do.
```
