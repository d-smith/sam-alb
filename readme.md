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
sam deploy --stack-name mf --template-file packaged.yml  --capabilities CAPABILTY_IAM
```


TODO - figure this out in cloud formation

To add using console:

EC2 - target groups, pick the once created in CF
Click targets, then create
Pick listener create via alb setup, edit routing rules: forward /hello to hello-lambda

And

aws lambda add-permission \ 
--function-name hwFunction \
--statement-id elb1 \
--principal elasticloadbalancing.amazonaws.com \
--action lambda:InvokeFunction \
--source-arn arn:aws:elasticloadbalancing:us-east-1:000011112222:targetgroup/hello-lambda/d2b38af5fc783473


