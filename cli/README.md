# Finmars Portfolio API CLI

A simple command-line interface for interacting with the Finmars Portfolio API.

## Installation

No additional installation required. The CLI uses the existing project dependencies.

## Configuration

Set the following environment variables:

```bash
# Required - API authentication token
export FINMARS_EXPERT_TOKEN='your-api-token-here'

# Optional - API configuration (defaults shown)
export FINMARS_BASE_URL=''
export FINMARS_REALM=''
export FINMARS_SPACE=''
```

## Usage

### Basic Commands

```bash
# List portfolios
python cli/main.py list-portfolios

# List portfolios with pagination
python cli/main.py list-portfolios --page 2 --page-size 20

# Get specific portfolio
python cli/main.py get-portfolio --id 123

# List portfolio types
python cli/main.py list-portfolio-types

# List portfolio history
python cli/main.py list-history

# Get portfolio reconciliation status
python cli/main.py portfolio-status

# Get status as JSON
python cli/main.py portfolio-status --json
```

### Running Examples

Run all example commands:

```bash
python cli/examples.py
```

This will demonstrate:
- Listing portfolios with pagination
- Getting portfolio details and attributes
- Working with portfolio types
- Accessing portfolio history
- Checking reconciliation status
- Getting first transaction dates

## Command Reference

### list-portfolios

List all portfolios with optional pagination and ordering.

```bash
python cli/main.py list-portfolios [--page PAGE] [--page-size SIZE] [--ordering FIELD]
```

Options:
- `--page`: Page number (default: 1)
- `--page-size`: Number of results per page (default: 10)
- `--ordering`: Field to order by (e.g., 'name', '-name' for descending)

### get-portfolio

Get details for a specific portfolio.

```bash
python cli/main.py get-portfolio --id PORTFOLIO_ID
```

Options:
- `--id`: Portfolio ID (required)

### list-portfolio-types

List all portfolio types.

```bash
python cli/main.py list-portfolio-types [--page PAGE] [--page-size SIZE] [--ordering FIELD]
```

Options:
- `--page`: Page number (default: 1)
- `--page-size`: Number of results per page (default: 10)
- `--ordering`: Field to order by

### list-history

List portfolio history records.

```bash
python cli/main.py list-history [--page PAGE] [--page-size SIZE] [--ordering FIELD]
```

Options:
- `--page`: Page number (default: 1)
- `--page-size`: Number of results per page (default: 10)
- `--ordering`: Field to order by

### portfolio-status

Get portfolio reconciliation status.

```bash
python cli/main.py portfolio-status [--json]
```

Options:
- `--json`: Output as JSON format

## Error Handling

The CLI will display error messages if:
- The `FINMARS_EXPERT_TOKEN` environment variable is not set
- API requests fail (network errors, authentication errors, etc.)
- Invalid command arguments are provided

## Development

To add new commands:

1. Add a new method to the `FinmarsCLI` class in `main.py`
2. Add argument parser configuration for the new command
3. Map the command to the method in the `command_map` dictionary
4. Optionally add examples to `examples.py`

## Tips

1. Set up an alias for convenience:
   ```bash
   alias finmars='python /path/to/finmars-ai-assistant/cli/main.py'
   ```

2. Export API token in your shell profile:
   ```bash
   # Add to ~/.bashrc or ~/.zshrc
   export FINMARS_EXPERT_TOKEN='your-token'
   ```

3. Use `--json` flag with `jq` for processing:
   ```bash
   python cli/main.py portfolio-status --json | jq '.key'
   ```