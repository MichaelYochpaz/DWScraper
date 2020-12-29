# Changelog
All notable changes to the script will be documented here.

## 1.0.2 - [2020-12-01]
### Added
* Issue URLs will now be generated in a more efficient method, with previous method being used as fallback.

### Bugfixes
* Fixed a small bug for when using a path that ends with a backwards slash.

## 1.0.1 - [2020-11-19]
### Bugfixes
* Added error handling so that the script can keep running even if there's an issue with one of the files.
* Fixed a few articles not being downloaded because of invalid characters in name.
* Fixed the year being set in different formats (sometimes as YY and sometimes as YYYY). Now it will always use the YYYY format.

## 1.0.0 - [2020-11-18]
* Initial release.
