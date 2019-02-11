#!/usr/bin/env python

import argparse
import os
import requests
import urllib3

from quads.config import conf as quads_config
from quads.quads import Api as QuadsApi
from quads.tools.foreman import Foreman

API = 'v2'


def main(argv=None):

    api_url = os.path.join(quads_config['quads_base_url'], 'api', API)
    quads = QuadsApi(api_url)

    urllib3.disable_warnings()

    if "data_dir" not in quads_config:
        print("quads: Missing \"data_dir\" in configuration.")
        exit(1)

    if "install_dir" not in quads_config:
        print("quads: Missing \"install_dir\" in configuration.")
        exit(1)

    if "quads_base_url" not in quads_config:
        print("quads: Missing \"quads_base_url\" in configuration.")
        exit(1)

    parser = argparse.ArgumentParser(description='Query current hosts marked for build')
    parser.add_argument('--cloud', dest='cloud', type=str, default=None, help='specify the cloud to query')

    args = parser.parse_args(argv)

    exitcode = 0
    # need to determine the ticket / password
    if args.cloud:
        # post
        cloud_details = quads.get_clouds(name=args.cloud)
        if 'ticket' in cloud_details:
            ticket_value = cloud_details["ticket"]

        if not ticket_value:
            ticket_value = quads_config['ipmi_password']

        foreman = Foreman(
            quads_config["foreman_api_url"],
            args.cloud,
            ticket_value,
        )

        hosts_to_build = foreman.get_parametrized("build", "true")

        if 'results' not in hosts_to_build:
            print("Unable to query foreman for cloud: " + args.cloud)
            print("Verify foreman password is correct: " + ticket_value)
            exitcode = 1
        else:
            if len(hosts_to_build['results']) > 0:
                print("The following hosts are marked for build:")
                print("")
            for h in hosts_to_build['results']:
                print(h['name'])
                exitcode = 1

    exit(exitcode)


if __name__ == "__main__":
    main()
