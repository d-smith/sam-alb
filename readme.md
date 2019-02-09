# sam-alb

Simple minded integration of lambda with ALB

## Notes

Local invoke

```console
sam local invoke HelloWorldFunction --event event.json --region us-east-1 --profile profile-name
```
## Self Signed Cert

What a pain... steps from [here](https://docs.aws.amazon.com/elasticbeanstalk/latest/dg/configuring-https-ssl.html) and [here](https://docs.aws.amazon.com/elasticbeanstalk/latest/dg/configuring-https-ssl-upload.html).
