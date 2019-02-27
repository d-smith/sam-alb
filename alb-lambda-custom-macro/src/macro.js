module.exports.handler = async (event, context) => {
    console.log(`event is ${JSON.stringify(event)}`);
    console.log(`context is ${JSON.stringify(context)}`);

    let retFragment = event['fragment'];
    delete retFragment.Resources.MyCustomResource

    console.log(`return fragment: ${JSON.stringify(retFragment)}`);
    return {
        "requestId": event["requestId"],
        "status": "SUCCESS",
        "fragment": retFragment
    }
}