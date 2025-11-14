---
order: 5
title: Contributing to this project
---

Thanks for visiting this page ! We are thankful for your consideration !

!!! info "Contibuting does not necessarly means coding"

    Indeed , taking the time to fill in a detailed issue for a bug or feature or proposing updates to the docs are also incredible ways you can support this project !

## ✨ Contribution Workflow

1. I create a detailed issue on a bug or a feature request and kindly propose my help
2. I fork the repo and create a branch to work on
3. I code and update / add unit tests
4. I run all unit tests
5. I merge my change back into the main repo with a **Pull Request**
6. I link the issues in the PR
7. your work will be reviewed and hopefully merged with all the thanks of the community

## 🛫 Setup

```bash
# create a venv
python -m venv .venv
# activate it
source .venv/bin/activate
# install dependencies ('pipx install poetry' if need be)
poetry install
```

## 🧪 Testing

Run the test suite:

```bash
pytest tests/
```
