# Unreleased

# v0.3.2
- Bugfix Added question mark in query parameter if needed

# v0.3.1
- Bugfix for multiple resolve items in one JSON
- Bugfix for version numbers as part of the directory structure

# v0.3.0
## API changes
- list_by_full_path considers deprecated = False by default
- list_by_full_subpath considers deprecated = False by default

## changes
- support deprecated flag in list_by_full_path and list_by_full_sub_path with False by default
- correct lint errors
- move to openid_client
- correct use of upload_fully_qualified flag
- identifier is recognized even in non fully qualified upload scenario
- pass alternative endpoint to http client to allow authorized access
- base is replaced by namespace to ensure contexts and resources are resolvable
- introduce hashcode for update checks
- provide entities self link and use it in upload utils
- instance creation failure in case of link missing is optional


# v0.2.0
- correct file structure
- add pylint support
- add pypi deployment on test server
- tests update and cleanups
- add code coverage report
- license header correction


# v0.1.3
- fix wrong endpoint when defining without env variables


# v0.1.2
- handle path, subpath build
- correct overridden namespace


# v0.1.1
- refactor uuid extraction method
- fix missing changes of new nexus structure
- fix namespace assignment


# v0.1.0
- add blazegraph client with documentation
- externalize configuration to env variables
- add timeouts to http requests
- support multiple identifiers for options
- add basic turtle support
- add deprecated restriction for resource resolution
- exclude deprecated resources for resolved elements
- introduce id caching for already resolved related instances
- add entities helpers and utils
- new schema versions
- use logger


# v0.0.2
- allow fully expanded contexts in the results
- include context support
- allow fully qualify json file
- data load fron data workbench
- refelction based schema generation
- new test data
- tier1 extension
- checksum calculation for diff-synx


# v0.0.1
- change resources in client
- restructure to repositories and entities


