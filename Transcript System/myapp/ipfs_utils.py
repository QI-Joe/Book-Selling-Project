import ipfshttpclient


def add_file_to_ipfs(file):
    with ipfshttpclient.connect() as client:
        result = client.add(file)
        return result["Hash"]
