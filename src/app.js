let headers = {};
headers['Content-Type']='application/json'

exports.lambdaHandler = async (event, context) => {

    console.log(`event: ${JSON.stringify(event)}`);
    console.log(`context: ${JSON.stringify(context)}`);

    return {
        statusCode: 200,
        statusDescription: 'HTTP OK',
        isBase64Encoded: false,
        body: JSON.stringify({greeting: 'hello'}),
        headers: headers
    }
};
