resource "aws_dynamodb_table" "audit_logs" {
  name         = "${var.project_name}-audit"
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "log_id"

  attribute {
    name = "log_id"
    type = "S"
  }

  tags = {
    Project = var.project_name
    Env     = var.environment
  }
}