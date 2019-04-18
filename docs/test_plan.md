# Mbed OS Tools Test Plan

The goal of delivering the unified Mbed OS tools is to improve testing and quality. We plan to deliver this by doing the following:

1. Preserve existing tests while migrating from the individual repositories to the unified repository
1. Begin gathering metrics in the continuous integration system to measure the initial state of the code and tests, as well as to measure future improvements
1. Bring up code coverage to a reasonable level
1. For core sections of the codebase, write [Black-box test cases](https://en.wikipedia.org/wiki/Black-box_testing) to enforce the current behavior (but remain agnostic to the implementation).
1. Begin refactoring the codebase to decrease duplication, remove unsupported APIs, and to set us up for future feature development
1. Establish a public facing (and documented) API
1. When the API has stabilized, release 1.0 and deprecate the legacy tools packages

## Existing test suite

The tools are currently in separate packages:

- `mbed-ls` (Mbed LS): https://pypi.org/project/mbed-ls
- `mbed-host-tests` (htrun): https://pypi.org/project/mbed-host-tests
- `mbed-greentea` (greentea): https://pypi.org/project/mbed-greentea

They all have their own test suites of varying completeness. Part of the effort of bringing these projects into the unified tools packages was to get these test suites passing consistently under all operating systems.

Once the test suites were all passing, their codebases were migrated to this repository (preserving the history through [git subtrees](https://git-scm.com/book/en/v1/Git-Tools-Subtree-Merging)). From there, the modules were moved to their current locations and the test suites were merged. The combined test suite is now ran on all PRs submitted to this repository in our continuous integration system.

### Preserving tests within the existing tools packages

Part of the delivery of the unified tools is to move the implementation out of the individual repositories. However, the existing packages need to preserve their API. They will do this by importing the `mbed-os-tools` package and reporting the necessary functions within their namespace.

Since the API of the existing tools packages is not changing, their tests should also still pass. Even though they are (for the most part) the same tests that were moved into `mbed-os-tools`, we will still ensure they pass before releasing them.

## Metrics

We are measuring code coverage in every PR. This allows us to gauge what the coverage was when moved the existing tools to the unified tools. It also provides metrics on how we are improving the quality of the tools going forward.

In addition to code coverage, we are in the process of enforcing consistent styling across the tools. This is not an insignificant effort since these tools were historically managed by different teams.

## Improving coverage

While the `detect` module has historically been well tested (~87% coverage), the `test` module has not (~44% coverage). The main focus going forward will be improving code coverage on the `test` module and building confidence in the tested interfaces.

## Black-box testing

Part of adding code coverage means writing the right tests for the job. We will implement the strategy of [black-box testing](https://en.wikipedia.org/wiki/Black-box_testing) when improving the code coverage. This allows us to enforce the behavior of the tools while decoupling the tests themselves from the implementation.

## Refactoring and the public API

These two efforts will go forward together. The goal is to refactor the current tools into a usable, Python API that anyone can import and use. This should happen iteratively, not in one big patch. This will give us time to test and integrate the new APIs into the existing tools packages if necessary.

## 1.0 release

When the API has stabilized, we will release 1.0 of this package and deprecate the legacy tools packages. When this happens, those repositories will be archived and the PyPI packages will not be updated. All users of the legacy tools should migrate to using the unified tools.
