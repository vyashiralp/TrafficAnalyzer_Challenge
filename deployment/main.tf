provider "aws" {
  profile    = "default"
  region     = var.region
  

}

resource "aws_s3_bucket" "web-traffic-artifacts" {

	bucket = var.bucket-name
	tags = var.resource-tags
	force_destroy = false
	acl = "private"
        
}

#create folder in s3 bucket 
resource "aws_s3_bucket_object" "InputFiles"{
bucket = var.bucket-name
acl= "private"
key = "input/"
depends_on = [aws_s3_bucket.web-traffic-artifacts]
}
resource "aws_s3_bucket_object" "OutputFiles"{
bucket = var.bucket-name
acl= "private"
key= "output/"
depends_on = [aws_s3_bucket.web-traffic-artifacts]
}


#create a role for Lambda
resource "aws_iam_role" "web-traffic-analysis_lambda_role" {
  name = var.wa-lambda-role
  tags = var.resource-tags
  assume_role_policy = <<POLICY
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "Service": "lambda.amazonaws.com"
      },
      "Action": "sts:AssumeRole"
    }
  ]
}
POLICY
}

#Create a policy for the lambda function
resource "aws_iam_policy" "wa_lambda_policy" {
name        = var.wa-lambda-policy
description = "Policy to add permission for sns,s3"


policy = <<EOF
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "lambda:InvokeFunction",
                "lambda:InvokeAsync"
            ],
            "Resource": "arn:aws:lambda:*:*:function:*"
        },
        {
            "Sid": "VisualEditor0",
            "Effect": "Allow",
            "Action": [
                "iam:*",
                "sns:*",
                "cloudwatch:*",
                "logs:*"
            ],
            "Resource": "*"
        },
        {
            "Sid": "VisualEditor1",
            "Effect": "Allow",
            "Action": [
                "sts:GetSessionToken",
                "sts:DecodeAuthorizationMessage",
                "sts:GetAccessKeyInfo",
                "sts:GetCallerIdentity"
            ],
            "Resource": "arn:aws:iam::*:role/web-traffic-analysis_lambda_role"
        },
        {
            "Sid": "VisualEditor3",
            "Effect": "Allow",
            "Action": "lambda:*",
            "Resource": [
                "arn:aws:lambda:us-west-2:*:function:web-traffic-analytics-function"
            ]
        },
        {
            "Sid": "VisualEditor4",
            "Effect": "Allow",
            "Action": [
                "s3:*",
                "s3:GetObject",
                "s3:PutObject",
                "s3:PutObjectAcl"
            ],
            "Resource": [
                "arn:aws:s3:::web-traffic-artifacts",
                "arn:aws:s3:::web-traffic-artifacts/*",
                "arn:aws:s3:::web-traffic-artifacts/input/*",
                "arn:aws:s3:::web-traffic-artifacts/output/*"
            ]
        }
    ]
}

EOF
}

#attach a policy to a role
resource "aws_iam_role_policy_attachment" "wa-lambda_policy_attachment" {
  role       = var.wa-lambda-policy-attachment
  policy_arn = "${aws_iam_policy.wa_lambda_policy.arn}"
}


#Create a Lambda function
resource "aws_lambda_function" "web-traffic-analytics-function" {
  filename = "WebTraffic.zip"
  function_name = var.wa-lambda-function
  role = "${aws_iam_role.web-traffic-analysis_lambda_role.arn}"
  handler = "lambda_function.lambda_handler"
  runtime = "python3.7"
  timeout = 900
  tags = var.resource-tags
  layers = ["${aws_lambda_layer_version.python37-wa-layer.arn}"]
  environment {
    variables = {
      wa_sns_topic_arn = "${aws_sns_topic.file_upload_topic.id}"
    }
  }
  }



#lambda layer
resource "aws_lambda_layer_version" "python37-wa-layer" {
  filename            = "my-lambda-layer/aws-layer/lambda-layer.zip"
  layer_name          = "Python37-wa-layer"
  compatible_runtimes = ["python3.7"]
}




#Create a permission for lambda to create event
resource "aws_lambda_permission" "wa_lambda-allow-bucket" {
  statement_id = "AllowExecutionFromS3Bucket"
  action = "lambda:InvokeFunction"
  function_name = "${aws_lambda_function.web-traffic-analytics-function.arn}"
  principal = "s3.amazonaws.com"
  source_arn = "${aws_s3_bucket.web-traffic-artifacts.arn}"
}


#Create a S3 put event
resource "aws_s3_bucket_notification" "wa_lambda-trigger" {
    bucket = "${aws_s3_bucket.web-traffic-artifacts.id}"
    lambda_function {
        lambda_function_arn = "${aws_lambda_function.web-traffic-analytics-function.arn}"
        events = ["s3:ObjectCreated:*"]
    }
}


#Create a SNS Topic for FILE UPLOAD application deployment

resource "aws_sns_topic" "file_upload_topic" {
  name = var.file_sns_topic_name
}

resource "aws_sns_topic_subscription" "file_upload_target" {
  topic_arn = aws_sns_topic.file_upload_topic.arn
  protocol  = "email"
  endpoint  = "hiralpvyas18@gmail.com"
}

