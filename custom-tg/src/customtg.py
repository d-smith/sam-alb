import json
import logging
import signal
from urllib2 import build_opener, HTTPHandler, Request


import os
import os.path
import sys
 
envLambdaTaskRoot = os.environ["LAMBDA_TASK_ROOT"]
print("LAMBDA_TASK_ROOT env var:"+os.environ["LAMBDA_TASK_ROOT"])
print("sys.path:"+str(sys.path))

sys.path.insert(0,envLambdaTaskRoot+"/botodeps")
print("sys.path:"+str(sys.path))

import boto3
import botocore
print("boto3 version:"+boto3.__version__)
print("botocore version:"+botocore.__version__)

LOGGER = logging.getLogger()
LOGGER.setLevel(logging.INFO)
client = boto3.client('elbv2')
lambdaClient = boto3.client('lambda')

def create_target_group(fnName):
    print('create target group')
    tgResponse = client.create_target_group(
                    Name=fnName,
                    HealthCheckEnabled=True,
                    HealthCheckPath='/health',
                    TargetType='lambda'
                )

    targetGroupArn = tgResponse['TargetGroups'][0]['TargetGroupArn']
    print('created target group %s', targetGroupArn)
    return targetGroupArn

def add_lambda_permission(fnName, targetGroupArn):
    lambdaPermResp = lambdaClient.add_permission(
                FunctionName=fnName,
                Action='lambda:InvokeFunction',
                Principal='elasticloadbalancing.amazonaws.com',
                SourceArn=targetGroupArn,
                StatementId='perm4tg'
            )

    print(lambdaPermResp)

def register_target(targetGroupArn, lambdaFnArn):
    regResponse = client.register_targets(
                        TargetGroupArn=targetGroupArn,
                        Targets=[
                            {
                                'Id': lambdaFnArn
                            },
                        ]
                    )

    print(regResponse)


def handler(event, context):
    '''Handle Lambda event from AWS'''
    # Setup alarm for remaining runtime minus a second
    signal.alarm((context.get_remaining_time_in_millis() / 1000) - 1)
    try:
        LOGGER.info('REQUEST RECEIVED:\n %s', event)
        LOGGER.info('REQUEST RECEIVED:\n %s', context)
        if event['RequestType'] == 'Create':
            LOGGER.info('CREATE!')
            fnName = event['ResourceProperties']['Function']
            LOGGER.info('Function name:\n %s', fnName)
            
            # Create target group
            targetGroupArn = create_target_group(fnName)

            # Create lambda permission
            add_lambda_permission(fnName, targetGroupArn)

            # Register target
            register_target(targetGroupArn, event['ResourceProperties']['FunctionArn'])

            send_response(event, context, "SUCCESS",
                          {"TargetGroupArn": targetGroupArn})
        elif event['RequestType'] == 'Update':
            LOGGER.info('UPDATE!')
            send_response(event, context, "SUCCESS",
                          {"Message": "Resource update successful!"})
        elif event['RequestType'] == 'Delete':
            LOGGER.info('DELETE!')
            fnName = event['ResourceProperties']['Function']
            LOGGER.info('Function name for target group delete:\n %s', fnName)

            response = client.describe_target_groups(
                    Names=[
                        fnName,
                    ]
                )

            targetGroupArn = response['TargetGroups'][0]['TargetGroupArn']
            LOGGER.info('target group arn for delete is %s', targetGroupArn)
            
            # Deregister targets
            deregResponse = client.deregister_targets(
                TargetGroupArn=targetGroupArn,
                Targets=[
                    {
                        'Id': event['ResourceProperties']['FunctionArn']
                    }
                ]
            )

            print(deregResponse)

            # Delete target group
            tgResponse = client.delete_target_group(
                            TargetGroupArn=targetGroupArn
                         )
            send_response(event, context, "SUCCESS",
                          {"Message": "Resource deletion successful!"})
        else:
            LOGGER.info('FAILED!')
            send_response(event, context, "FAILED",
                          {"Message": "Unexpected event received from CloudFormation"})
    except: #pylint: disable=W0702
        LOGGER.info('FAILED!')
        LOGGER.info( sys.exc_info()[0])
        LOGGER.info( sys.exc_info()[1])
        LOGGER.info( sys.exc_info()[2])
        send_response(event, context, "FAILED", {
            "Message": "Exception during processing"})


def send_response(event, context, response_status, response_data):
    '''Send a resource manipulation status response to CloudFormation'''
    response_body = json.dumps({
        "Status": response_status,
        "Reason": "See the details in CloudWatch Log Stream: " + context.log_stream_name,
        "PhysicalResourceId": context.log_stream_name,
        "StackId": event['StackId'],
        "RequestId": event['RequestId'],
        "LogicalResourceId": event['LogicalResourceId'],
        "Data": response_data
    })

    LOGGER.info('ResponseURL: %s', event['ResponseURL'])
    LOGGER.info('ResponseBody: %s', response_body)

    opener = build_opener(HTTPHandler)
    request = Request(event['ResponseURL'], data=response_body)
    request.add_header('Content-Type', '')
    request.add_header('Content-Length', len(response_body))
    request.get_method = lambda: 'PUT'
    response = opener.open(request)
    LOGGER.info("Status code: %s", response.getcode())
    LOGGER.info("Status message: %s", response.msg)


def timeout_handler(_signal, _frame):
    '''Handle SIGALRM'''
    raise Exception('Time exceeded')


signal.signal(signal.SIGALRM, timeout_handler)