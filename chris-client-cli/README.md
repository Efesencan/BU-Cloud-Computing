# ChRIS Client CLI Application
## Installation
`bash install.sh`

## Usage
```
Usage: chrisclient [OPTIONS]

Options:
  --username TEXT                 Username for ChRIS (default: 'chris')
  --password TEXT                 Password for ChRIS (default: 'chris1234')
  --address TEXT                  Address for ChRIS (default: 'http://localhost:8000/api/v1/')
  --get_plugin_details <TEXT TEXT>...
                                  Get a plugin's details. Pass in type first
                                  (plugin_id or plugin_name) then the
                                  argument.
                                  
  --list_compute_resources        List the compute resources
  --get_compute_resources_details
                                  Get the details of the compute resource
  --list_installed_plugins        List the installed plugins
  --help                          Show this message and exit.
```
