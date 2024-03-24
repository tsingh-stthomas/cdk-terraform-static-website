#!/usr/bin/env python
from constructs import Construct
from cdktf import App, TerraformStack, TerraformOutput
from imports.aws import AwsProvider, S3, Cloudfront, CloudfrontDistribution, S3BucketObject, S3BucketWebsite

class CdkTerraformStaticWebsiteStack(TerraformStack):
    def __init__(self, scope: Construct, ns: str):
        super().__init__(scope, ns)

        # Define AWS provider
        AwsProvider(self, "Aws", region="us-east-1")

        # Define S3 bucket for website hosting
        website_bucket = S3.Bucket(
            self, "WebsiteBucket",
            website_configuration=[{
                "index_document": "index.html",
                "error_document": "error.html"
            }]
        )

        # Define CloudFront distribution
        distribution = CloudfrontDistribution(
            self, "Distribution",
            origin=[CloudfrontDistribution.OriginArgs(
                domain_name=website_bucket.bucket_regional_domain_name,
                origin_id="s3Origin",
                custom_origin_config=[CloudfrontDistribution.CustomOriginConfigArgs(
                    http_port=80,
                    https_port=443,
                    origin_protocol_policy="http-only"
                )]
            )],
            default_cache_behavior=[CloudfrontDistribution.DefaultCacheBehaviorArgs(
                target_origin_id="s3Origin",
                viewer_protocol_policy="redirect-to-https"
            )]
        )

        # Output the website URL
        self.website_url = distribution.domain_name_output

app = App()
CdkTerraformStaticWebsiteStack(app, "cdk-terraform-static-website")
app.synth()
