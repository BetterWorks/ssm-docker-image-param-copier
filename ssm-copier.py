import argparse
import boto3

parser = argparse.ArgumentParser()
parser.add_argument("-s", "--source", action="store", dest="source",
                    help="Source application, e.g., sandbox")
parser.add_argument("-d", "--destination", action="store", dest="destination",
                    help="Destination application name, e.g., sandbox5")
parser.add_argument("-e", "--environment", action="store", dest="environment",
                    help="Environment/AWS account/stage, e.g., sandbox")
parser.add_argument("-l", "--latest", action="store_true", default=False,
                    help="Use latest as tag for all Docker images. Default is False.",
                    dest="latest")
args = parser.parse_args()

def get_secure_string_params(source, environment, next_token=None):
    if next_token:
        params = client.describe_parameters(
            ParameterFilters=[
                {
                    'Key': 'Name',
                    'Option': 'BeginsWith',
                    'Values': [
                        '/bw/' + args.environment + '/betterworks-' + args.source +
                        '/cicd/deployment/manifest/',
                    ]
                },
                {
                    'Key': 'Type',
                    'Option': 'Equals',
                    'Values': [
                        'SecureString',
                    ]
                },
            ],
            MaxResults=10,
            NextToken=next_token,
        )   
        if 'NextToken' in params.keys():
            return params['Parameters'], params['NextToken']
        else:
            return params['Parameters'], None
    else:
        params = client.describe_parameters(
            ParameterFilters=[
                {
                    'Key': 'Name',
                    'Option': 'BeginsWith',
                    'Values': [
                        '/bw/' + args.environment + '/betterworks-' +
                        args.source + '/cicd/deployment/manifest/',
                    ]
                },
                {
                    'Key': 'Type',
                    'Option': 'Equals',
                    'Values': [
                        'SecureString',
                    ]
                },
            ],
            MaxResults=10,
        )   
        return params['Parameters'], params['NextToken']

def get_string_params(source, environment, next_token=None):
    if next_token:
        params = client.describe_parameters(
            ParameterFilters=[
                {
                    'Key': 'Name',
                    'Option': 'BeginsWith',
                    'Values': [
                        '/bw/' + args.environment + '/betterworks-' + 
                        args.source + '/cicd/deployment/manifest/',
                    ]
                },
                {
                    'Key': 'Type',
                    'Option': 'Equals',
                    'Values': [
                        'String',
                    ]
                },
            ],
            MaxResults=10,
            NextToken=next_token,
        )   
        if 'NextToken' in params.keys():
            return params['Parameters'], params['NextToken']
        else:
            return params['Parameters'], None
    else:
        params = client.describe_parameters(
            ParameterFilters=[
                {
                    'Key': 'Name',
                    'Option': 'BeginsWith',
                    'Values': [
                        '/bw/' + args.environment + '/betterworks-' +
                        args.source + '/cicd/deployment/manifest/',
                    ]
                },
                {
                    'Key': 'Type',
                    'Option': 'Equals',
                    'Values': [
                        'String',
                    ]
                },
            ],
            MaxResults=10,
        )   
        return params['Parameters'], params['NextToken']

def put_secure_string_params(destination, environment, source_param_names,
                            source_param_values):
    for param, value in zip(source_param_names, source_param_values):
        param_name, param_value = (param, value)
        print('Copying parameter {}'.format(param_name))
        response = client.put_parameter(
            Name='/bw/' + environment + '/betterworks-' +
            destination + '/cicd/deployment/manifest/' + param_name,
            Value=param_value,
            Type='SecureString',
            KeyId='alias/bw-' + args.environment + '-chamber',
            Overwrite=True,
        )

def put_string_params(destination, environment, source_param_names,
                            source_param_values):
    for param, value in zip(source_param_names, source_param_values):
        param_name, param_value = (param, value)
        print('Copying parameter {}'.format(param_name))
        response = client.put_parameter(
            Name='/bw/' + environment + '/betterworks-' +
            destination + '/cicd/deployment/manifest/' + param_name,
            Value=param_value,
            Type='String',
            Overwrite=True,
        )

client = boto3.client('ssm')

string_results = []

params, next_token  = get_string_params(args.source, args.environment)

for param in params:
    string_results.append(param['Name'])

while next_token is not None:
    params, next_token = get_string_params(args.source, args.environment, next_token=next_token)
    for param in params:
        string_results.append(param['Name'])

secure_string_results = []

params, next_token  = get_secure_string_params(args.source, args.environment)

for param in params:
    secure_string_results.append(param['Name'])

while next_token is not None:
    params, next_token = get_secure_string_params(args.source, args.environment, next_token=next_token)
    for param in params:
        secure_string_results.append(param['Name'])

string_param_names = []

for param in string_results:
    string_param_names.append(param.split('/')[-1])

secure_string_param_names = []

for param in secure_string_results:
    secure_string_param_names.append(param.split('/')[-1])

string_param_values = []

for param in string_results:
    value = client.get_parameter(Name=param)
    if args.latest:
        if 'image_tag' in param:
            string_param_values.append('latest')
        else:
            string_param_values.append(value['Parameter']['Value'])
    else:
        string_param_values.append(value['Parameter']['Value'])

secure_string_param_values = []

for param in secure_string_results:
    value = client.get_parameter(Name=param, WithDecryption=True)
    if args.latest:
        if 'image_tag' in param:
            secure_string_param_values.append('latest')
        else:
            secure_string_param_values.append(value['Parameter']['Value'])
    else:
        secure_string_param_values.append(value['Parameter']['Value'])

put_secure_string_params(args.destination, args.environment,
                         secure_string_param_names, secure_string_param_values)

put_string_params(args.destination, args.environment,
                  string_param_names, string_param_values)

print('Done!')
