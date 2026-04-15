resource "aws_s3_bucket" "audit_bucket" {
  bucket = "${var.project_name}-audit-bucket"
}

resource "aws_s3_bucket_versioning" "versioning" {
  bucket = aws_s3_bucket.audit_bucket.id

  versioning_configuration {
    status = "Enabled"
  }
}