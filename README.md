# Lumi Chatbot Webhook

This project is part of the Lumi Chatbot initiative.
Webhook actions for the chatbot interface

## Getting Started

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes.

### Prerequisites

This project consideres only Unix based OSes, running **Python 3.7.6** as the default Python version.
A different version of Python might cause the requirements installation to fail.
The rest of these instructions will consider the use of `Linux Ubuntu 16.04`.
Follow the steps below to install the required packages to run the project.

1. Install Pip, Venv and Git

```
sudo apt-get update && sudo apt-get install -y python3-pip python3-venv git
```

2. Install Poetry

```
curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py | python
```

### Installing

Please follow the step by step series of instructions below to get the development environment ready.

1. Clone repository

```
git clone git@github.com:lumichatbot/webhook.git lumi-webhook
```

2.  Install project dependencies

```
cd lumi-webhook
poetry install
```

2.  Activate project virtual environment

```
poetry shell
```

## Deployment

TBD

## Authors

-   **Arthur Jacobs** - _Initial work_ - [asjacobs92](https://github.com/asjacobs92)

## Citing Lumi
```
@inproceedings{Jacobs2021,
    author = {Arthur S. Jacobs and Ricardo J. Pfitscher and Rafael H. Ribeiro and Ronaldo A. Ferreira and Lisandro Z. Granville and Walter Willinger and Sanjay G. Rao},
    title = {Hey, Lumi! Using Natural Language for Intent-Based Network Management},
    booktitle = {2021 {USENIX} Annual Technical Conference ({USENIX} {ATC} 21)},
    year = {2021},
    isbn = {978-1-939133-23-6},
    pages = {625--639},
    url = {https://www.usenix.org/conference/atc21/presentation/jacobs},
    publisher = {{USENIX} Association},
    month = jul,
}
```
