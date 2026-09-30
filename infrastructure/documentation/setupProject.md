# SET UP THE PROJECT

1. fill up the backend.hcl to save the backend in a remote station, in this case we use a S3 bucket. To do this you need to be authenticated in your terminal with AWS CLI.

2. run
```bash
terraform init -backend-config="backend.hcl"
```
***Be aware that you are running this commands from `/infrastructure` folder***