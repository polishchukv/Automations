output "dmz_instance_public_ip" {
  value = aws_instance.dmz.public_ip
}

output "internal_instance_1_private_ip" {
  value = aws_instance.internal_1.private_ip
}

output "internal_instance_2_private_ip" {
  value = aws_instance.internal_2.private_ip
}

output "internal_instance_3_private_ip" {
  value = aws_instance.internal_3.private_ip
}

output "bastion_instance_public_ip" {
  value = aws_instance.bastion.public_ip
}
