resource "aws_s3_bucket" "tf_state" {
  bucket = "smart-locker-tf-state"

  lifecycle {
    prevent_destroy = false  # Temporarily disabled for destruction
  }
}

resource "aws_dynamodb_table" "tf_locks" {
  name         = "tf-locks"
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "LockID"

  attribute {
    name = "LockID"
    type = "S"
  }
}