# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html) after the 1.0.0 release.

## 0.5.0 - 2022-02-20

### Changed

-   Changed the OAuth helper classes (#136)

## 0.4.0 - 2022-02-19

### Added

-   Added `get_devices_by_type` to `Room` entity (#102)
-   Add way to get entity type easily  (#102)
-   Improve entity creation and visibility for unsupported entities (#107)
-   Improve token refresh (#131)
-   Improve OAuth layer (#133)

## 0.3.1 - 2021-10-15

### Fixed

-   Fix dependency bug

## 0.3.0 - 2021-10-13

### Added

-   Add `AsyncOAuthHandler`

### Fixed

-   Fix type on `valve_position` on `RadiatorValve`

### Changed

-   Changed `get_credentials.py` to handle whole payload

## 0.2.0 - 2021-10-07

### Added

-   Add `find_device_by_identifier` to discovered

## 0.1.1 - 2021-10-07

### Changed

-   Make client async functions non-private

## 0.1.0 - 2021-10-06

Initial release.
