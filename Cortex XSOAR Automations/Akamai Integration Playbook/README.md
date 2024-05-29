# Akamai Integration Playbook

This repository contains a Cortex XSOAR playbook designed for Akamai integration. The playbook allows interaction with Akamai's network lists via API calls to retrieve, list, and manage IP addresses within network lists.

## Table of Contents

- [Akamai Integration Playbook](#akamai-integration-playbook)
  - [Table of Contents](#table-of-contents)
  - [Description](#description)
  - [Intended Environment](#intended-environment)
  - [Setup](#setup)
  - [Features](#features)
  - [Usage](#usage)
  - [API Endpoints](#api-endpoints)
  - [Functionality](#functionality)
  - [Error Handling](#error-handling)
  - [Logging](#logging)
  - [License](#license)
  - [Contact](#contact)

## Description

This Cortex XSOAR playbook integrates with Akamai to enrich and manage network lists. It provides a set of commands to query, list, and add IP addresses to network lists.

## Intended Environment

This integration is intended to be run within a Security Orchestration, Automation, and Response (SOAR) environment, specifically designed and tested for Cortex XSOAR.

## Setup

1. **Clone the Repository**
    ```sh
    git clone https://github.com/polishchukv/akamai-integration-playbook.git
    cd akamai-integration-playbook
    ```

2. **Configuration**
    - Set up the integration configuration in Cortex XSOAR with the following parameters:
      - URL
      - Client Token
      - Client Secret
      - Access Token
      - Proxy (if required)

## Features

- Fetch network lists from Akamai.
- Retrieve detailed information for a specific network list.
- Add IP addresses to network lists.
- Test the connectivity and validity of the integration.

## Usage

### Commands available:

1. `test-module`:
    - Tests the connectivity and validity of the integration.

2. `akamai-show-network-lists`:
    - Retrieves a specific network list by provided `list-id`.

3. `akamai-list-network-lists`:
    - Lists all available network lists.

4. `akamai-add-ip-to-list`:
    - Adds an IP address to a specified network list.

```sh
# Example command format:
!akamai-show-network-lists list-id=exampleListId
```

## API Endpoints

This playbook uses the following API endpoints from Akamai:

- `https://api.crowdstrike.com/oauth2/token`: OAuth2 token retrieval
- `/network-list/v2/network-lists`: For retrieving network lists
- `/network-list/v2/network-lists/{list_id}/elements`: For adding IP addresses to network lists

## Functionality

### Authentication

- Utilizes OAuth2 for authentication. Retrieves and uses a Bearer token for API requests.

### Initialization

- Configures the requests session with EdgeGridAuth for secure API communication.
- Initializes the logger for tracking and debugging.

### Network List Operations

- **Retrieve Network List**: Fetches a detailed network list by ID.
- **List Network Lists**: Lists all available network lists.
- **Add IP to List**: Adds an IP address to the specified network list.

## Error Handling

- Catches and logs HTTP errors and other exceptions.
- Raises appropriate errors for issues like missing parameters.

## Logging

- Initializes logging at the INFO level.
- Logs all key operations and error messages for easy debugging and monitoring.