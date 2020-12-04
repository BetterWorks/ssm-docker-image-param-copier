import argparse
import boto3
import os.path

parser = argparse.ArgumentParser()
parser.add_argument("-s", "--source", action="store", dest="source",
                    help="Source application, e.g., sandbox")
parser.add_argument("-sf", "--source-file", action="store", dest="source_file",
                    help="Use file as source, e.g., -sf /tmp/source_file.csv. Incompatible with -s.")
parser.add_argument("-d", "--destination", action="store", dest="destination",
                    help="Destination application name, e.g., sandbox5")
parser.add_argument("-df", "--destination-file", action="store", dest="destination_file",
                    help="Copy params to a file, e.g., -df /tmp/dest_file.csv. Incompatible with -d.")
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
        print('Copying parameter {}'.format(param))
        response = client.put_parameter(
            Name='/bw/' + environment + '/betterworks-' +
            destination + '/cicd/deployment/manifest/' + param,
            Value=value,
            Type='SecureString',
            KeyId='alias/bw-' + args.environment + '-chamber',
            Overwrite=True,
        )

def put_string_params(destination, environment, source_param_names,
                            source_param_values):
    for param, value in zip(source_param_names, source_param_values):
        print('Copying parameter {}'.format(param))
        response = client.put_parameter(
            Name='/bw/' + environment + '/betterworks-' +
            destination + '/cicd/deployment/manifest/' + param,
            Value=value,
            Type='String',
            Overwrite=True,
        )


def read_params_from_file(source_file):
    string_param_names = []
    string_param_values = []
    secure_string_param_names = []
    secure_string_param_values = []
    
    lines = open(source_file, "r")
    
    for line in lines:
        params = line.split(',')
        
        if params[2] == 'String\n':
            string_param_names.append(params[0])
            string_param_values.append(params[1])
        
        elif params[2] == 'SecureString\n':
            secure_string_param_names.append(params[0])
            secure_string_param_values.append(params[1])
            
    return string_param_names, string_param_values, secure_string_param_names, secure_string_param_values


def write_params_to_file(source_param_names, source_param_values, source_param_type):
    if os.path.isfile(args.destination_file):
        print('Destination file already exists. Exiting.')
        exit(1)
    
    with open(args.destination_file, 'a') as filehandle:
        for param, value in zip(source_param_names, source_param_values):
            print('Writing {} parameter, type {}'.format(param, source_param_type))
            if args.latest:
                if 'image_tag' in param:
                    filehandle.write('{},{},{}\n'.format(param, 'latest', source_param_type))
                else:
                    filehandle.write('{},{},{}\n'.format(param, value, source_param_type))
            else:
                filehandle.write('{},{},{}\n'.format(param, value, source_param_type))


if (args.source and args.source_file) or (args.destination and args.destination_file):
    print('Incompatible options, exiting.')
    exit(1)

string_results = []
string_param_names = []
string_param_values = []
secure_string_results = []
secure_string_param_names = []
secure_string_param_values = []

client = boto3.client('ssm')

if args.source:
    params, next_token  = get_string_params(args.source, args.environment)
    
    for param in params:
        string_results.append(param['Name'])
    
    while next_token is not None:
        params, next_token = get_string_params(args.source, args.environment, next_token=next_token)
        for param in params:
            string_results.append(param['Name'])
    
    params, next_token  = get_secure_string_params(args.source, args.environment)
    
    for param in params:
        secure_string_results.append(param['Name'])
    
    while next_token is not None:
        params, next_token = get_secure_string_params(args.source, args.environment, next_token=next_token)
        for param in params:
            secure_string_results.append(param['Name'])
    
    for param in string_results:
        string_param_names.append(param.split('/')[-1])
    
    for param in secure_string_results:
        secure_string_param_names.append(param.split('/')[-1])

    for param in string_results:
        value = client.get_parameter(Name=param)
        if args.latest:
            if 'image_tag' in param:
                string_param_values.append('latest')
            else:
                string_param_values.append(value['Parameter']['Value'])
        else:
            string_param_values.append(value['Parameter']['Value'])

    for param in secure_string_results:
        value = client.get_parameter(Name=param, WithDecryption=True)
        if args.latest:
            if 'image_tag' in param:
                secure_string_param_values.append('latest')
            else:
                secure_string_param_values.append(value['Parameter']['Value'])
        else:
            secure_string_param_values.append(value['Parameter']['Value'])

elif args.source_file:
    param_names, param_values, secure_param_names, secure_param_values = read_params_from_file(args.source_file)
    
    if (secure_param_names and secure_param_values):
        for param, value in zip(param_names, param_values):
            string_param_names.append(param)
            string_param_values.append(value)

    if (param_names and param_values):
        for param, value in zip(param_names, param_values):
            string_param_names.append(param)
            string_param_values.append(value)
    
else:
    print('No source or source file specified. Exiting.')
    exit(1)
    
if args.destination:
    if (string_param_names and string_param_values):
        put_string_params(args.destination, args.environment,
                         string_param_names, string_param_values)
    
    if (secure_string_param_names and secure_string_param_values):
        put_secure_string_params(args.destination, args.environment,
                                secure_string_param_names, secure_string_param_values)

    print('Done!')

elif args.destination_file:
    if (string_param_names and string_param_values):
        write_params_to_file(string_param_names, string_param_values, 'String')
    
    if (secure_string_param_names and secure_string_param_values):
        write_params_to_file(secure_string_param_names, secure_string_param_values, 'SecureString')
    
    print('Done!')
    
else:
    print('No destination or destination file specified. Exiting.')
    exit(1)
