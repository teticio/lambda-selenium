terraform {
  required_providers {
    aws = {
      source = "hashicorp/aws"
    }

    docker = {
      source = "kreuzwerker/docker"
    }
  }
}

provider "aws" {
  profile = var.profile
  region  = var.region
}

data "aws_caller_identity" "this" {}

data "aws_ecr_authorization_token" "token" {}

provider "docker" {
  registry_auth {
    address  = format("%v.dkr.ecr.%v.amazonaws.com", data.aws_caller_identity.this.account_id, var.region)
    username = data.aws_ecr_authorization_token.token.user_name
    password = data.aws_ecr_authorization_token.token.password
  }
}

module "lambda_selenium" {
  source                 = "terraform-aws-modules/lambda/aws"
  count                  = var.num_proxies
  function_name          = "selenium-${count.index}"
  create_package         = false
  image_uri              = module.docker_image.image_uri
  package_type           = "Image"
  architectures          = ["x86_64"]
  timeout                = 30
  memory_size            = 4096
  ephemeral_storage_size = 4096
  hash_extra             = count.index
}

module "docker_image" {
  source          = "terraform-aws-modules/lambda/aws//modules/docker-build"
  create_ecr_repo = true
  ecr_repo        = "lambda-selenium"
  source_path     = "${path.module}"
  platform        = "linux/amd64"

  image_tag = sha1(join("", [
    filesha1("${path.module}/lambda_function.py"),
    filesha1("${path.module}/Dockerfile")
  ]))

  ecr_repo_lifecycle_policy = jsonencode({
    "rules" : [
      {
        "rulePriority" : 1,
        "description" : "Keep only the last 1 image",
        "selection" : {
          "tagStatus" : "any",
          "countType" : "imageCountMoreThan",
          "countNumber" : 1
        },
        "action" : {
          "type" : "expire"
        }
      }
    ]
  })
}
