# Hevy API
This Python module is a lightweight wrapper around the [Hevy API](https://api.hevyapp.com/docs). From their website:
>   Welcome to Hevy's public API! We're just starting to roll this out and depending on your feedback, we'll be adding more features and endpoints. Also, we make no guarantees that we won't completely change the structure or abandon the project entirely so use it at your own risk.

That being said, please [open an issue](https://github.com/remuzel/hevy-api/issues/new) if you see any feature drifts between this and the official docs.

## [Model Context Protocol](https://modelcontextprotocol.io/) (MCP) Server

This Python client was initially destined to support an MCP Server for Hevy, but the amazing [@chrisdoc](https://github.com/chrisdoc) beat me to it! Check it out on Github or Smithery:

[![GitHub](https://img.shields.io/badge/GitHub-hevy--mcp-blue?logo=github)](https://github.com/chrisdoc/hevy-mcp) [![smithery badge](https://smithery.ai/badge/@chrisdoc/hevy-mcp)](https://smithery.ai/server/@chrisdoc/hevy-mcp)

## Installation

### For development
```bash
uv sync --dev && uv pip install -e .
```

### For use
```bash
uv add git+https://github.com/remuzel/polarsteps-api.git
```

### API Key

Currently, the Hevy API is only made available to Hevy Pro users (via an API key), and hence so is this module.

You can get your key at https://hevy.com/settings?developer and set it as an environment variable:
```bash
export HEVY_API_KEY='your_api_key'
```

## Quick Start
```python
from hevy_api.client import HevyClient
from hevy_api.models.model import Workout

# Initialize the client
client = HevyClient()

# Example Workout
last_workout: Workout | None = (client.get_workouts().workouts or [None])[-1]
if last_workout is None:
    exit("Could not find workouts.")
print(last_workout.summary)
```
