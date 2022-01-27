# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

import os
import sys
import json
import re
import urllib3

import boto3
import requests
from requests_aws4auth import AWS4Auth

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def get_endpoint_url_from_ssm(session, region):
    ssm_client = session.client(
        'ssm',
        region_name=region
    )

    response = ssm_client.get_parameter(
        Name='/MRE/ControlPlane/EndpointURL',
        WithDecryption=True
    )

    assert "Parameter" in response

    endpoint_url = response["Parameter"]["Value"]
    endpoint_url_regex = ".*.execute-api."+region+".amazonaws.com/api/.*"

    assert re.match(endpoint_url_regex, endpoint_url)

    return endpoint_url


class RegisterPlugin:
    def __init__(self, region, profile=None):
        self.session = boto3.session.Session(profile_name=profile)
        self.credentials = self.session.get_credentials()
        self.auth = AWS4Auth(
            self.credentials.access_key,
            self.credentials.secret_key,
            region,
            'execute-api',
            session_token=self.credentials.token
        )
        self.endpoint_url = get_endpoint_url_from_ssm(self.session, region)
    
    def invoke_controlplane_api(self, path, method, headers=None, body=None, params=None):
        print(f"{method} {path}")

        response = requests.request(
            method=method,
            url=self.endpoint_url + path,
            params=params,
            headers=headers,
            data=body,
            verify=False,
            auth=self.auth
        )

        response.raise_for_status()

        return response

    def get_model_by_name(self, name):
        try:
            path = f"/model/{name}"
            method = "GET"

            api_response = self.invoke_controlplane_api(path, method)

        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 404:
                raise Exception(f"Model '{name}' not found in MRE")

        except requests.exceptions.RequestException as e:
            raise Exception(f"Encountered an exception while getting the model '{name}' from MRE: {str(e)}")

        else:
            return api_response.json()

    def get_model_by_name_and_version(self, name, version):
        try:
            path = f"/model/{name}/version/{version}"
            method = "GET"

            api_response = self.invoke_controlplane_api(path, method)

        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 404:
                raise Exception(f"Model '{name}' with version '{version}' not found in MRE")

        except requests.exceptions.RequestException as e:
            raise Exception(f"Encountered an exception while getting the model '{name}' with version '{version}' from MRE: {str(e)}")

    def get_plugin_by_name(self, name):
        try:
            path = f"/plugin/{name}"
            method = "GET"

            api_response = self.invoke_controlplane_api(path, method)

        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 404:
                raise Exception(f"DependentPlugin '{name}' not registered in MRE")

        except requests.exceptions.RequestException as e:
            raise Exception(f"Encountered an exception while getting the plugin '{name}' from MRE: {str(e)}")
    
    def register_plugin(self, plugin_config):
        # Check if all the ModelEndpoints exist in MRE
        if "ModelEndpoints" in plugin_config and plugin_config["ModelEndpoints"]:
            for index, model_endpoint in enumerate(plugin_config["ModelEndpoints"]):
                if "Version" in model_endpoint:
                    self.get_model_by_name_and_version(model_endpoint["Name"], model_endpoint["Version"])
                else:
                    api_response = self.get_model_by_name(model_endpoint["Name"])
                    plugin_config["ModelEndpoints"][index]["Version"] = f"v{api_response['Latest']}"

        # Check if all the DependentPlugins are registered in MRE
        if "DependentPlugins" in plugin_config and plugin_config["DependentPlugins"]:
            for plugin in plugin_config["DependentPlugins"]:
                self.get_plugin_by_name(plugin)

        path = "/plugin"
        method = "POST"
        
        headers = {
            "Content-Type": "application/json"
        }

        api_response = self.invoke_controlplane_api(path, method, headers=headers, body=json.dumps(plugin_config))
        
        return api_response.json()


def execute(region, profile=None):
    cdk_outputs = open('cdk-outputs.json', 'r')
    cdk_outputs_json = json.loads(cdk_outputs.read())

    print("Initializing the RegisterPlugin class")
    register_obj = RegisterPlugin(region, profile)

    plugins = [name for name in os.listdir('../Plugins') if os.path.isdir(os.path.join('../Plugins', name))]
    indep_plugins = []

    print("Registering all the Plugins that are not dependent on other Plugins")

    # Step 1: Loop through the Plugins directory and register all the Plugins that are not dependent on other Plugins
    for plugin_name in plugins:
        try:
            with open(f'../Plugins/{plugin_name}/config.json') as f:
                plugin_config = json.load(f)

                if "DependentPlugins" not in plugin_config["MRE"]["Plugin"]:
                    indep_plugins.append(plugin_name)
                    
                    print(f"Adding {plugin_name} Lambda ARN to the config file")
                    plugin_config["MRE"]["Plugin"]["ExecuteLambdaQualifiedARN"] = cdk_outputs_json["aws-mre-plugin-samples"][plugin_name]

                    print(f"Registering {plugin_name} Lambda as a Plugin in MRE")
                    print(register_obj.register_plugin(plugin_config["MRE"]["Plugin"]))

        except Exception as e:
            print("!!!!")
            print(f"ERROR in registering {plugin_name} Lambda as a Plugin in MRE: {str(e)}")
            print("!!!!")

    print("Registering all the Plugins that are dependent on other Plugins")

    # Step 2: Loop through the Plugins directory and register all the Plugins that are dependent on other Plugins
    for plugin_name in plugins:
        if plugin_name not in indep_plugins:
            try:
                with open(f'../Plugins/{plugin_name}/config.json') as f:
                    print(f"Adding {plugin_name} Lambda ARN to the config file")

                    plugin_config = json.load(f)
                    plugin_config["MRE"]["Plugin"]["ExecuteLambdaQualifiedARN"] = cdk_outputs_json["aws-mre-plugin-samples"][plugin_name]

                    print(f"Registering {plugin_name} Lambda as a Plugin in MRE")
                    print(register_obj.register_plugin(plugin_config["MRE"]["Plugin"]))

            except Exception as e:
                print("!!!!")
                print(f"ERROR in registering {plugin_name} Lambda as a Plugin in MRE: {str(e)}")
                print("!!!!")

    return 1


if __name__ == '__main__':
    if len(sys.argv) == 3:
        result = execute(sys.argv[1], sys.argv[2])
    else:
        result = execute(sys.argv[1])

    sys.exit(0) if result else sys.exit(1)
