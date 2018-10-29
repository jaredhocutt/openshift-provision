#!/usr/bin/env bash

ec2_regions=$(aws ec2 describe-regions --query 'Regions[].{Name:RegionName}' --output text)

echo "ec2_ami_ids:"

for ec2_region in ${ec2_regions};
do
  echo "  ${ec2_region}:"

  access_images=($(aws ec2 describe-images --owners 309956199498 --query 'Images[*].[ImageId]' --filters "Name=name,Values=RHEL-7.5?*GA*Access*" --region ${ec2_region} --output text | sort -r))
  echo "    cloud_access: ${access_images[0]}"
  hourly_images=($(aws ec2 describe-images --owners 309956199498 --query 'Images[*].[ImageId]' --filters "Name=name,Values=RHEL-7.5?*GA*Hourly*" --region ${ec2_region} --output text | sort -r))
  echo "    hourly: ${hourly_images[0]}"
done
