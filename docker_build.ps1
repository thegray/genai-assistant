# step 1: build lambda package inside Docker
docker run --rm -it `
  -v ${PWD}:/var/task `
  -w /var/task `
  --entrypoint /bin/bash `
  public.ecr.aws/lambda/python:3.12 `
  -c "bash build_lambda.sh"

# step 2: zip using native PowerShell
Compress-Archive -Path .\lambda_package\* -DestinationPath .\lambda_deploy.zip -Force
