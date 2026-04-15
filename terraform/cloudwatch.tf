resource "aws_cloudwatch_log_group" "fog_logs" {
  name              = "/fog/smart-locker"
  retention_in_days = 30
}