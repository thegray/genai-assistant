docker run --rm -it `
  -v ${PWD}:/var/task `
  -w /var/task `
  --entrypoint /bin/bash `
  public.ecr.aws/lambda/python:3.12 `
  -c "bash build_lambda.sh"
