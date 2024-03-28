# LargeFieldAnalyzer - Malware Scanning Documentation

## Accessing the Malware Dashboard

To access the Malware Dashboard, visit [leto.gg](https://leto.gg) and log in. Upgrade to the Business Plan to unlock the Malware Dashboard feature.

## Introduction to Malware Scanning

The LargeFieldAnalyzer provides two methods to scan your content for malware. To initiate a scan, the content must be publicly accessible for our system to retrieve. This can be achieved using an IPFS node or a public server.

### Preparing Your Content for Analysis

To analyze your content for malware, ensure it is formatted correctly:

- For direct scanning, provide a Content Identifier (CID) or a URL Address.
- To submit logs for analysis, your logs should be a `.csv` file where each line contains a separate piece of content, identified by a CID or URL.

### Scanning Options

#### Option 1: Direct Content Submission

Submit the IPFS/Filecoin CID of the specific content you wish to scan through our dashboard. This method is suitable for individual content items.

#### Option 2: Bulk Content Scanning

For scanning large volumes of content, upload a `.CSV` file to our dashboard. The file should contain IPFS/Filecoin CIDs or URLs, one per line. This option is designed for publicly hosted data and facilitates bulk scanning efficiently.
