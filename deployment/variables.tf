variable "region" {
  default = "us-west-2"
}

variable "resource-tags" {
  description = "Tags to set for all resources"
  type        = "map"
  default     = {
    project     = "WebTrafficAnalysis",
    environment = "dev",
	contact = "hiralpvyas18@gmail.com"
  }
}
variable "bucket-name"{
  description = "Name of the s3 bucket for web traffic analysis"
  default     = "website-traffic-artifacts"
}
variable "wa-lambda-role"{
	default =  "web-traffic-analysis_lambda_role"
}


variable "wa-lambda-policy"{
  default = "wa_lambda_policy"
}
variable "wa-lambda-policy-attachment"{
  default= "web-traffic-analysis_lambda_role"
}
variable "wa-lambda-function"{
  default= "web-traffic-analytics-function"
}

variable "wa-lambda-profile"{
  default="wa-profile"
}

variable "WA_SNS_subscription_email_address_list" {
   type = list(string)
   description = "List of email addresses"
   default = ["hiralpvyas18@gmail.com"]
 }
 

variable "sns_topic_arn"{
  default = "arn:aws:sns:us-west-2:729500115754:ITD_ERA_SNS_FILE_UPLOAD"
}

variable "sns_subscription_protocol" {
  type = string
  default = "email"
  description = "SNS subscription protocal"
}


variable "file_sns_topic_name" {
  type = string
  description = "SNS topic name"
  default = "WA_SNS"
}

variable "file_sns_topic_display_name" {
  type = string
  description = "SNS topic display name"
  default = "WA_SNS"
}




