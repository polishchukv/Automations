# FalconHost Endpoint Enrichment Playbook

This repository contains a Cortex XSOAR playbook designed to enrich endpoint data using CrowdStrike FalconHost. The playbook automates the process of retrieving and verifying device details based on a given hostname.

## Playbook ID

`20gdc190-b7d4-4892-9df8-f2be4fef8b4b`

## Description

The FalconHost Endpoint Enrichment playbook retrieves device information from CrowdStrike FalconHost based on a provided hostname. It verifies if the device exists and retrieves detailed information about the device if it is found.

## Intended Environment

This playbook is intended to be run within a SOAR (Security Orchestration, Automation, and Response) environment, specifically designed and tested for Cortex XSOAR.

## Overview

### Start Task

The playbook begins with a start task that transitions to the next task immediately.

### Task 1: Retrieve Device Hostname

- **Task ID**: `9c1d13d3-cc4f-4ed6-9c7d-8c456d6a7355`
- **Description**: Retrieves the CrowdStrike device ID based on the hostname.
- **Script**: `FalconHost|||cs-device-search`
- **Next Task**: Task 2

### Task 2: Is device present?

- **Task ID**: `b993c9f9-993b-4ea9-945c-3dd9ea59311b`
- **Description**: Verifies if any machine matches the hostname.
- **Type**: Condition
- **Next Task**:
  - If device is found: Task 4
  - Else: Task 3

### Task 3: Finished

- **Task ID**: `60b27104-b151-4162-809c-5d6e5783f596`
- **Description**: Marks the playbook as finished if no device is found.

### Task 4: Retrieve host details from FalconHost

- **Task ID**: `23b9424f-03d9-4524-9ab5-949781e97f33`
- **Description**: Retrieves detailed host information from FalconHost if the device is found.
- **Script**: `FalconHost|||cs-device-details`
- **Next Task**: Task 3 (Finished)

## Inputs

- **Hostname**: The hostname to enrich (Optional)
  - Context Path: `Endpoint.Hostname`

## Outputs

- **Endpoint.Hostname**: The hostname enriched (string)
- **Endpoint.OS**: The operating system of the endpoint (string)
- **Endpoint.IP**: List of endpoint IP addresses
- **Endpoint.MAC**: List of endpoint MAC addresses
- **Endpoint.Domain**: The domain name of the endpoint (string)

## Tasks Breakdown

1. **Task 0: Start Task**
   - **Type**: Start
   - **Description**: Initiates the playbook.
   - **Position**: `x: 50, y: 50`

2. **Task 1: Retrieve Device Hostname**
   - **Type**: Regular
   - **Description**: Retrieves the CrowdStrike device ID based on the hostname.
   - **Position**: `x: 50, y: 200`
   - **Script Arguments**:
     - `query`: `${incident.dest}`

3. **Task 2: Is device present?**
   - **Type**: Condition
   - **Description**: Verifies if any machine matches the hostname.
   - **Position**: `x: 50, y: 350`
   - **Condition**:
     - `label`: "yes"
     - `condition`:
       - operator: `isExists`
       - left:
         - `value`: `FalconHostDevices`
         - `iscontext`: true

4. **Task 3: Finished**
   - **Type**: Title
   - **Description**: Marks the playbook as finished if no device is found.
   - **Position**: `x: 50, y: 700`

5. **Task 4: Retrieve host details from FalconHost**
   - **Type**: Regular
   - **Description**: Retrieves detailed host information from FalconHost if the device is found.
   - **Position**: `x: 300, y: 500`
   - **Script Arguments**:
     - `ids`: `${FalconHostDevices}`

## Visualization

The playbook is visualized with the tasks positioned as follows:
- **Start**: `x: 50, y: 50`
- **Retrieve Device Hostname**: `x: 50, y: 200`
- **Is device present?**: `x: 50, y: 350`
- **Finished**: `x: 50, y: 700`
- **Retrieve host details from FalconHost**: `x: 300, y: 500`