import json
import logging
import signal
from urllib2 import build_opener, HTTPHandler, Request


import os
import os.path
import sys

logger = logging.getLogger()
logger.setLevel(logging.INFO)

envLambdaTaskRoot = os.environ["LAMBDA_TASK_ROOT"]
sys.path.insert(0,envLambdaTaskRoot+"/botodeps")

import boto3
import botocore
logger.info("boto3 version: %s", boto3.__version__)
logger.info("botocore version: %s", botocore.__version__)


client = boto3.client('elbv2')
lambdaClient = boto3.client('lambda')

def create_target_group(fnName):
    logger.info('create target group')
    tgResponse = client.create_target_group(
                    Name=fnName,
                    HealthCheckEnabled=True,
                    HealthCheckPath='/health',
                    TargetType='lambda'
                )

    targetGroupArn = tgResponse['TargetGroups'][0]['TargetGroupArn']
    logger.info('created target group %s', targetGroupArn)
    return targetGroupArn

def add_lambda_permission(fnName, targetGroupArn):
    logger.info('create lambda permission')
    lambdaPermResp = lambdaClient.add_permission(
                FunctionName=fnName,
                Action='lambda:InvokeFunction',
                Principal='elasticloadbalancing.amazonaws.com',
                SourceArn=targetGroupArn,
                StatementId='perm4tg'
            )


def register_target(targetGroupArn, lambdaFnArn):
    logger.info('register target %s', lambdaFnArn)
    regResponse = client.register_targets(
                        TargetGroupArn=targetGroupArn,
                        Targets=[
                            {
                                'Id': lambdaFnArn
                            },
                        ]
                    )


def target_group_to_delete(fnName):
    response = client.describe_target_groups(
                    Names=[
                        fnName,
                    ]
                )

    targetGroupArn = response['TargetGroups'][0]['TargetGroupArn']
    logger.info('target group arn for delete is %s', targetGroupArn)
    return targetGroupArn
    
def dergister_target(targetGroupArn, lambdaFnArn):
    logger.info('dergister target %s', lambdaFnArn)
    client.deregister_targets(
        TargetGroupArn=targetGroupArn,
        Targets=[
            {
                'Id': lambdaFnArn
            }
        ]
    )

def delete_target_group(targetGroupArn):
    logger.info('delete target group %s', targetGroupArn)
    client.delete_target_group(
        TargetGroupArn=targetGroupArn
    )
    

def handler(event, context):
    '''Handle Lambda event from AWS'''
    # Setup alarm for remaining runtime minus a second
    signal.alarm((context.get_remaining_time_in_millis() / 1000) - 1)
    try:
        logger.info('REQUEST RECEIVED:\n %s', event)
        logger.info('REQUEST RECEIVED:\n %s', context)
        if event['RequestType'] == 'Create':
            logger.info('CREATE!')
            fnName = event['ResourceProperties']['Function']
            logger.info('Function name:\n %s', fnName)
            
            # Create target group
            targetGroupArn = create_target_group(fnName)

            # Create lambda permission
            add_lambda_permission(fnName, targetGroupArn)

            # Register target
            register_target(targetGroupArn, event['ResourceProperties']['FunctionArn'])

            send_response(event, context, "SUCCESS",
                          {"TargetGroupArn": targetGroupArn})
        elif event['RequestType'] == 'Update':
            logger.info('UPDATE!')
            send_response(event, context, "SUCCESS",
                          {"Message": "Resource update successful!"})
        elif event['RequestType'] == 'Delete':
            logger.info('DELETE!')
            fnName = event['ResourceProperties']['Function']
            logger.info('Function name for target group delete:\n %s', fnName)

            targetGroupArn = target_group_to_delete(fnName)
            
            # Deregister targets
            dergister_target(targetGroupArn, event['ResourceProperties']['FunctionArn'])
            
            # Delete target group
            delete_target_group(targetGroupArn)

            send_response(event, context, "SUCCESS",
                          {"Message": "Resource deletion successful!"})
        else:
            logger.info('FAILED!')
            send_response(event, context, "FAILED",
                          {"Message": "Unexpected event received from CloudFormation"})
    except: #pylint: disable=W0702
        logger.info('FAILED!')
        logger.info( sys.exc_info()[0])
        logger.info( sys.exc_info()[1])
        logger.info( sys.exc_info()[2])
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

    logger.info('ResponseURL: %s', event['ResponseURL'])
    logger.info('ResponseBody: %s', response_body)

    opener = build_opener(HTTPHandler)
    request = Request(event['ResponseURL'], data=response_body)
    request.add_header('Content-Type', '')
    request.add_header('Content-Length', len(response_body))
    request.get_method = lambda: 'PUT'
    response = opener.open(request)
    logger.info("Status code: %s", response.getcode())
    logger.info("Status message: %s", response.msg)


def timeout_handler(_signal, _frame):
    '''Handle SIGALRM'''
    raise Exception('Time exceeded')


signal.signal(signal.SIGALRM, timeout_handler)