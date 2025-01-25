# Vsports API

## FILE: /vsports/vsports/README.md

### This file contains the documentation for the Vsports API package

The Vsports API is a Python package that provides an interface for interacting with the Vsports API. It allows users to access various endpoints and retrieve sports-related data efficiently.

## Features

- Access to multiple endpoints of the Vsports API.
- Support for caching using Redis to improve performance.
- Easy-to-use methods for retrieving events, teams, and other sports data.

## Installation

You can install the Vsports API package using pip:

```bash
pip install vsports
```

## Usage

Here is a simple example of how to use the Vsports API:

```python
import json
from vsports import VsportsAPI

MYTOKEN = "your_token_here"
redis_config = {
    "host": "localhost", 
    "port": 6379, 
    "db": 0,
    "ttl": 300
}

vsports = VsportsAPI(MYTOKEN, redis_config=redis_config)
result = vsports.events_by_date("2025-01-24", usecache=True)
if result:
    print(json.dumps(result, indent=2))

result = vsports.teams_by_tournament(118, usecache=True)
if result:
    for team in result:
        print(team['name'])
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
