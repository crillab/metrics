# Contributing Guidelines

Contributions to this project are welcome!
You will find below useful information if you wish to contribute.

## How is *Metrics* developed?

### Development Tools

*Metrics-Scalpel* is written in [Python 3](https://www.python.org) using
JetBrain's [*PyCharm*](https://www.jetbrains.com/pycharm/) as IDE.
You are obviously free to use any other IDE, provided that you do not push any
personal configuration file on this repository.

### Development Best Practices

In this project, we try to follow development best practices.

Because this requires to execute many different tasks, we have gathered them
all in a `Makefile` to make easier their execution.
The available targets are described below.

#### Unit Tests

Unit tests are written with the built-in module
[`unittest`](https://docs.python.org/fr/3.8/library/unittest.html), and are run
using [`nose`](https://nose.readthedocs.io/en/latest/).

To execute these unit tests with code coverage, execute the following command
after having installed the `nose` module:

```bash
make test
```

Test reports are displayed in the terminal, and are also stored in the
`build` folder.

#### Static Code Analysis

Static code analysis is performed with both [`pylint`](https://www.pylint.org)
and [SonarQube](https://www.sonarqube.org).

To run the `pylint` analysis, install the corresponding module and then execute
the following command:

```bash
make pylint
```

The violations are displayed in the terminal, and the report is also stored in
the `build` folder.

To run the SonarQube analysis, install
[`sonar-scanner`](https://docs.sonarqube.org/latest/analysis/scan/sonarscanner/)
and then execute the following command:

```bash
make sonar
```

The report will be uploaded to the SonarQube instance specified to
`sonar-scanner`.

#### PyPI Targets

**This section is intended for *Metrics-Scalpel's* developers only.**

The `metrics` module is available on [PyPI](https://pypi.org), and
managed with [`setuptools`](https://pypi.org/project/setuptools/).

To register the module, execute the following command:

```bash
make register
```

To create an archive of the last version of the module, execute the following
command:

```bash
make package
```

To publish the last version of the module, execute the following command:

```bash
make upload
```

## Introducing New Features

When using *Metrics-Scalpel*, you may miss some features.
You can submit a *feature request* or a *merge request* for them.

Note that new features have to be useful for most of the users, and should not
introduce (too many) breaking changes.

### Submitting a Feature Request

You can submit a feature request by writing an issue tagged with the label
**Feature Request**.
In this issue, try to describe *precisely* what you want, by using examples if
possible.

We will evaluate the feature you ask for, to see whether it is feasible and
useful for the users.
If so, we will consider its implementation.

### Implementing Features

You may also want to implement the features you miss.
If you want to share your implementation, you will need to fork this project
and to submit a *merge request*.

When writing the merge request, try to describe *precisely* what you have
implemented.
If the feature was initially submitted as a feature request, specify also the
corresponding issue using `#X`, where `X` is the number of the issue.

We will only accept merge requests satisfying the following conditions:

+ The feature you implemented is properly documented to help people understand
  what it does and how to use it.
+ You have written enough unit tests along with your implementation.
+ No breaking changes are introduced, unless your feature requires them.
+ Your implementation is easily readable, and does not trigger any avoidable
  linter warning.

If one of these conditions is not satisfied, you will be asked to apply the
changes required to satisfy it.

Note that we may reject some features.
We are open-minded, and rejections are not definitive: we might finally accept
the feature after discussions, or if many users support it.
However, we advise you to have at most one implemented feature per request
(unless they are dependent on each other), so that we can still accept some of
the features while rejecting others.

## Bug Fixing

While using *Metrics-Scalpel*, you may find bugs that you may want to either
*report* or *fix*.

### Reporting a Bug

To report a bug, just submit an issue tagged with the label **Bug**.

Try to describe as precisely as possible the problem you have encountered.
In particular, we need the following information:

+ What is the expected behaviour?
+ What is the actual behaviour?

If possible, also attach a minimal example so that we can easily reproduce the
bug.

### Fixing a Bug

You may also fix the bug yourself, and submit a merge request with your fix.

Before writing the fix, ask yourself whether the bug you identified is actually
a bug.
If you are not sure, prefer submitting a bug report first.
Otherwise, we will reject the merge request.

When submitting the request, start by describing the bug you have fixed.
If this bug has already been reported, specify the corresponding issue using
`#X`, where `X` is the number of the issue.
Otherwise, describe in your message the bug you have fixed, as for a bug
report.

The conditions for your merge request to be accepted are the following:

+ Again, the bug you fixed is indeed a bug.
+ Unless unavoidable, no breaking changes are introduced.
+ You have written non-regression tests proving that your fix works.
+ Your fix is easily readable, and does not trigger any avoidable linter
  warning.

If one of these conditions is not satisfied, you will be asked to apply the
changes required to satisfy it.
