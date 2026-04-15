# Multi-layer Security

Multi-layer Security is a smart locker security project that combines fog computing, multi-factor authentication, anomaly detection, and cloud audit logging.

The system is built around a Python-based fog node that performs:

- RFID-based user identification
- Alphanumeric PIN verification
- OTP verification with Twilio Verify or local TOTP fallback
- Behavioral anomaly detection using a machine learning model
- Local log buffering with background synchronization to AWS

## Project Structure

- `fog_node/` - Main fog-layer application and supporting modules
- `datasets/` - CSV datasets used for user generation and ML model training
- `terraform/` - Infrastructure-as-code for AWS resources such as DynamoDB, S3, IAM, and CloudWatch

## Features

- Multi-factor authentication using RFID, PIN, and OTP
- Fog-layer decision making for low-latency access control
- Rate limiting and lockout handling for repeated failures
- ML-based anomaly detection for suspicious access attempts
- Cloud audit persistence using DynamoDB and S3
- Offline-friendly logging with later sync to cloud services

## Tech Stack

- Python
- boto3
- Twilio Verify
- scikit-learn
- pandas
- Terraform
- AWS DynamoDB
- AWS S3
- AWS CloudWatch

## How It Works

1. A user scans an RFID tag.
2. The system validates the RFID against the local user database.
3. The user enters an alphanumeric PIN.
4. The system sends and verifies an OTP.
5. The fog node checks behavioral context with an ML anomaly detector.
6. The system grants or denies access.
7. Access logs are stored locally and synced to AWS in the background.

## Requirements

- Python 3.10+ recommended
- AWS credentials if cloud sync is enabled
- Twilio credentials if SMS OTP is enabled
- Terraform installed if you want to provision the AWS infrastructure

## Installation

Clone the repository:

```bash
git clone https://github.com/Adarsh-Narayan17/Multi-layer-Security.git
cd Multi-layer-Security
```

Install Python dependencies:

```bash
cd fog_node
pip install -r requirements.txt
```

## Configuration

### Twilio

Set these environment variables if you want real SMS OTP:

```bash
TWILIO_ACCOUNT_SID=your_account_sid
TWILIO_AUTH_TOKEN=your_auth_token
TWILIO_VERIFY_SERVICE_SID=your_verify_service_sid
```

If Twilio is not configured, the app falls back to local OTP generation for demo/testing.

### AWS

Configure AWS credentials before using cloud sync:

```bash
AWS_ACCESS_KEY_ID=your_access_key
AWS_SECRET_ACCESS_KEY=your_secret_key
AWS_DEFAULT_REGION=ap-south-1
```

## Running the Fog Node

From the `fog_node` directory:

```bash
python main.py
```

You will be prompted for:

- RFID tag
- PIN
- OTP

## Supporting Scripts

Inside `fog_node/`:

- `generate_users.py` - Generates a local test user database from dataset values
- `manual_sync.py` - Manually triggers upload of unsynced local logs
- `test_aws_connection.py` - Checks AWS connectivity and permissions
- `test_access_flow.py` - Simulates access attempts for testing
- `verify_aws_logs.py` - Verifies whether logs were stored in AWS
- `show_test_results.py` - Displays a summary of recent AWS test results
- `ml/train_model.py` - Trains the anomaly detection model from dataset files

## Terraform Infrastructure

The `terraform/` folder contains configuration for provisioning cloud resources such as:

- DynamoDB audit table
- S3 audit bucket
- IAM roles and policies
- CloudWatch resources

To use it:

```bash
cd terraform
terraform init
terraform plan
terraform apply
```

## Notes

- Local secrets and Terraform state files are excluded from version control.
- The committed `users.json` contains sanitized sample values for safe public sharing.
- Pretrained ML artifacts are included so the project can run without retraining first.

## Future Improvements

- Add a web or mobile dashboard
- Improve package/module naming from `_init_.py` to `__init__.py`
- Add automated unit and integration tests
- Add Docker support
- Add CI/CD for linting, tests, and deployment

## License

Add a license file if you want to define reuse terms for this project.
