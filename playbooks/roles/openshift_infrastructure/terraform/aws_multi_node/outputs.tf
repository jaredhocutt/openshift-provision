output "master_instance" {
  value = aws_instance.master
}

output "infra_instance" {
  value = aws_instance.infra
}

output "compute_instances" {
  value = [for i in aws_instance.compute : i]
}

output "master_eip" {
  value = aws_eip.master
}

output "infra_eip" {
  value = aws_eip.infra
}
