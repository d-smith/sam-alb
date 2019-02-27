# sam-alb

Simple minded integration of lambda with ALB

## Notes

Local invoke

```console
sam local invoke HelloWorldFunction --event event.json --region us-east-1 --profile profile-name
```
## Self Signed Cert

What a pain... steps from [here](https://docs.aws.amazon.com/elasticbeanstalk/latest/dg/configuring-https-ssl.html) and [here](https://docs.aws.amazon.com/elasticbeanstalk/latest/dg/configuring-https-ssl-upload.html).


## Deploy

Create a vps stack, then an alb stack, then...

```console
sam package --template-file template.yml --s3-bucket sampack-97068 > packaged.yml
sam deploy --stack-name mf --template-file packaged.yml  --capabilities CAPABILITY_IAM
```

Deploy the lambda - review the settings in the Makefile, then:

```console
make
```

Creating the target is not supported in cloud formation at the moment (TODO - verify this). Use the cli to finish things:

Create the target group:

```console
aws elbv2 create-target-group \
--name hello-lambda \
--target-type lambda \
--health-check-enabled \
--health-check-path /hello
```

Note the target group arn from the output - you need this to add permissions and register the target. You will also need the lambda ARN.

Add permission:

```console
aws lambda add-permission \
--function-name hwFunction \
--statement-id elb1 \
--principal elasticloadbalancing.amazonaws.com \
--action lambda:InvokeFunction \
--source-arn arn:aws:elasticloadbalancing:us-east-1:000011112222:targetgroup/hello-lambda/1bcc30c57e645c80
```

Register the target:

```console
aws elbv2 register-targets \
--target-group-arn arn:aws:elasticloadbalancing:us-east-1:000011112222:targetgroup/hello-lambda/1bcc30c57e645c80 \
--targets Id=arn:aws:lambda:us-east-1:000011112222:function:hwFunction
```

Add a rule:

```console
aws elbv2 create-rule \
--listener-arn arn:aws:elasticloadbalancing:us-east-1:000011112222:listener/app/geoffry/1a7bc1fd290c73b7/6bbc80adaeea67e0 \
--conditions Field=path-pattern,Values=/hello \
--priority 1 \
--actions Type=forward,TargetGroupArn=arn:aws:elasticloadbalancing:us-east-1:000011112222:targetgroup/hello-lambda/1bcc30c57e645c80
```


## Custom Resource

Exploring using a custom resource to create the target group. Learned the node SDK does not support lambda targets.

