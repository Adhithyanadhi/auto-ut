# AutoUT

Features

> Generate unit test cases automatically for service functions.

## How to use

Click on Generate UT on the function name and wait till the toast message appears with new coverage.

## Requirements

Requires Python3

VSC version ^1.86.0.

resources.TestCase

set absolute path to load config.env in config.go

## Extension Settings

No special settings required.

## Known Issues

- interface type conversion. Eg: Data.(string)
- function with filterInput, map[any_type]interface{} parameter is not handled
- function with orchestrator
- same function called more than once in the same function

## Release Notes

Initial version with base code coverage.

### 0.0.1

Initial release AutoUT.

### 0.0.2

Minor bugfixes

### 0.0.8

Handled empty function input and output arguments.

## For more information

* [GitHub](https://github.com/Adhithyanadhi/auto-ut)

**Enjoy AutoUT!**
