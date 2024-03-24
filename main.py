#!/usr/bin/env python
from constructs import Construct
from cdktf import App, TerraformStack, TerraformOutput
from imports.aws import AwsProvider, S3Bucket, Cloudfront, CloudfrontDistribution, S3BucketObject, S3BucketWebsite

class CdkTerraformStaticWebsiteStack(TerraformStack):
    def __init__(self, scope: Construct, ns: str):
        super().__init__(scope, ns)

        # Define AWS provider
        AwsProvider(self, "Aws", region="us-east-1")

        # Define S3 bucket for website hosting
        website_bucket = S3Bucket(
            self, "WebsiteBucket",
            acl="public-read",
            website_bucket=[
                S3BucketWebsite(
                    error_document="error.html", index_document="index.html"
                )]
        )
        
        # Define local path to a index.html file to upload
        s3_file_source = "/Users/tsingh/aiml/path/to/website/files/index.html"
        mimetype, _ = mimetypes.guess_type(s3_file_source) # Guess mimetype of the file for S3 upload
        
        # Upload the index.html file to the S3 bucket with public-read ACL for use in a static website
        bucket_object = S3BucketObject(
            self,
            "s3_bucket_object_indexhtml",
            depends_on=[website_bucket],
            bucket=website_bucket.bucket,
            key="index.html",
            acl="public-read",
            source=s3_file_source,
            content_type=mimetype
        ) 
        
        # Define CloudFront distribution to sit in front of the S3 bucket holding the website contents
        cloudfront_distribution = CloudfrontDistribution(
            self, "Distribution",
            enabled=True,
            default_root_object="index.html",
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
        TerraformOutput(self, "out_s3_bucket_website_url", value=website_bucket.bucket_regional_domain_name)
        TerraformOutput(self, "out_cloudfront_distribution_domain_name", value=cloudfront_distribution.domain_name)

    
app = App()
CdkTerraformStaticWebsiteStack(app, "cdk-terraform-static-website")
    
# Deploy stack
app.synth()