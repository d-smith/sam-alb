
var AWS = require('aws-sdk');

//aws elbv2 create-target-group \
//--name hello-lambda \
//--target-type lambda \
//--health-check-enabled \
//--health-check-path /hello

exports.handler = function (event, context) {

    console.log("REQUEST RECEIVED:\n" + JSON.stringify(event));

    // For Delete requests, immediately send a SUCCESS response.
    if (event.RequestType == "Delete") {
        sendResponse(event, context, "SUCCESS");
        return;
    }

    let result = {
        "foo":"yep"
    }

    let fnName = event.ResourceProperties.Function;
    console.log(`create target group for ${fnName}`);

    var elbv2 = new AWS.ELBv2();
    let params = {
        Name: `${fnName}-tg`,
        TargetType: 'lambda',
        HealthCheckEnabled: true,
        HealthCheckPath: '/health'
    }

    let createPromise = elbv2.createTargetGroup(params).promise();
    createPromise.then(function(data){
        console.log(`tg ok: ${JSON.stringify(data)}`);
    }).catch(function(err) {
        console.log(err);
    })


    var responseStatus = "SUCCESS";
    sendResponse(event, context, responseStatus, result);
};

// Send response to the pre-signed S3 URL 
function sendResponse(event, context, responseStatus, responseData) {

    var responseBody = JSON.stringify({
        Status: responseStatus,
        Reason: "See the details in CloudWatch Log Stream: " + context.logStreamName,
        PhysicalResourceId: context.logStreamName,
        StackId: event.StackId,
        RequestId: event.RequestId,
        LogicalResourceId: event.LogicalResourceId,
        Data: responseData
    });

    console.log("RESPONSE BODY:\n", responseBody);

    var https = require("https");
    var url = require("url");

    var parsedUrl = url.parse(event.ResponseURL);
    var options = {
        hostname: parsedUrl.hostname,
        port: 443,
        path: parsedUrl.path,
        method: "PUT",
        headers: {
            "content-type": "",
            "content-length": responseBody.length
        }
    };

    console.log("SENDING RESPONSE...\n");

    var request = https.request(options, function (response) {
        console.log("STATUS: " + response.statusCode);
        console.log("HEADERS: " + JSON.stringify(response.headers));
        // Tell AWS Lambda that the function execution is done  
        context.done();
    });

    request.on("error", function (error) {
        console.log("sendResponse Error:" + error);
        // Tell AWS Lambda that the function execution is done  
        context.done();
    });

    // write data to request body
    request.write(responseBody);
    request.end();
}