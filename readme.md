# sam-alb

Simple integration of lambda with ALB, with custom cloud formation resource to hook the lambda up to an ALB.

## Deployment

Note that you must carefully examine the default parameter settings in the cloud formation templates and override them as needed when installing cloud formation or SAM resources.

### ALB Set Up

This project assumes a situation where you want to install a lambda into an account that is already configured with a VPC and ALB. 

If you do not have such an environment...

1. Create a VPC for the ALB using the `vpc.yml` template in the `alb-setup` directory.
2. Install a certificate into the ACM for your ALB configuration.
3. Create the ALB using the `alb.yml` template in the `alb-setup` directory.

If you need to create a self signed certificate, follow the  steps [here](https://docs.aws.amazon.com/elasticbeanstalk/latest/dg/configuring-https-ssl.html) and [here](https://docs.aws.amazon.com/elasticbeanstalk/latest/dg/configuring-https-ssl-upload.html).

### Cloud Formation Custom Resource

To deploy this stack, you must first deploy the custom resource lambda in the custom-tg directory. To do so, customize the `Makefile` then deploy via `make`.

*Note* - the first time you deploy the project you must first do a `make dependencies` to pip install the latest versions of boto3 and botocore as they are required to support lambda targets; the current lambda runtime in AWS has an older version of boto3 that does not support this.

### ALB Fronted Lambda

With the custom lambda installed, update the `Makefile` to reflect your set up then `make`to install.



## Notes

### Local invoke

```console
    sam local invoke HelloWorldFunction --event event.json --region us-east-1 --profile profile-name
```

### Custom Resource

* Custom resource was needed as current cloud formation does not support lambda targets for target groups.
* First tried writing the custom resource using NodeJS, but when I ran it it did not support lambda targets... I did not verify the SDK version in the lambda runtime so it is possible it was a version lag not missing functionality in the SDK.
* After abandoning a Node JS implementation (perhaps prematurely), discovered the python SDK version in the lambda environment lags the version of the SDK needed for lambda targets. Modified the project to upload the latest SDK version - see [this](https://www.mandsconsulting.com/lambda-functions-with-newer-version-of-boto3-than-available-by-default/) for details.
* I used an interactive python notebook to work through the SDK calls to install and uninstall the target group, configure the listener, etc.