output "dynamodb_table" {
  value = aws_dynamodb_table.audit_logs.name
}

output "s3_bucket" {
  value = aws_s3_bucket.audit_bucket.bucket
}

output "iam_role" {
  value = aws_iam_role.fog_role.name
}