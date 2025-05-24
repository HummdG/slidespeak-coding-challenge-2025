## Prerequisites

- Having Docker installed on your system.

## Running the docker container

```bash
docker compose up --build
```

## AWS Setup

1. **IAM User**

   - **Name:** `ppt-to-pdf-bot`
   - **ARN:** `arn:aws:iam::769998260308:user/ppt-to-pdf-bot`
   - **Permissions:** Attached policy `AmazonS3FullAccess` (grants S3 upload/download)

2. **S3 Bucket**

   - **Name:** `hummdg-ppt2pdf`
   - **Region:** `eu-west-1`

3. **AWS CLI Configuration**
   ```bash
   aws configure
   AWS Access Key ID [None]: <ASK_FOR_THIS_INSTRUCTIONS>
   AWS Secret Access Key [None]: <ASK_FOR_THIS_INSTRUCTIONS>
   Default region name [None]: eu-west-1
   Default output format [None]: json
   ```
