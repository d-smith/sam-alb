deploy:
	sam package --template-file template.yml --s3-bucket sampack-97068 --output-template-file packaged.yml
	sam deploy --stack-name customtg --template-file packaged.yml --capabilities CAPABILITY_IAM

dependencies:
	cd src && pip install -r requirements.txt -t ./botodeps && cd ..
