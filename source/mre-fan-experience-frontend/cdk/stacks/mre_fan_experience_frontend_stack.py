# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

from aws_cdk import (
    core,
    aws_iam,
    aws_codecommit,
    aws_amplify,
    aws_cognito
)


class MreFanExperienceFrontendStack(core.Stack):
    def __init__(self, scope: core.Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        # region Cognito
        user_pool = aws_cognito.UserPool(
            self, "MRE-fan-experience-frontend",
            user_pool_name="MRE-fan-experience-frontend"
        )

        admin_email = core.CfnParameter(self, "adminemail", type="String")

        aws_cognito.CfnUserPoolUser(
            self, "CognitoUser",
            user_pool_id=user_pool.user_pool_id,
            desired_delivery_mediums=["EMAIL"],
            user_attributes=[{
                "name": "email",
                "value": admin_email.value_as_string
            }],
            username="Admin"
        )

        user_pool_client = aws_cognito.UserPoolClient(
            self, "MRE-fan-experience-frontend-UserPoolClient",
            user_pool=user_pool
        )

        identity_pool = aws_cognito.CfnIdentityPool(
            self, "MRE-fan-experience-frontend-IdentityPool",
            identity_pool_name="MRE-fan-experience-frontend-IdentityPool",
            cognito_identity_providers=[{
                "clientId": user_pool_client.user_pool_client_id,
                "providerName": user_pool.user_pool_provider_name
            }],
            allow_unauthenticated_identities=False
        )

        unauthenticated_role = aws_iam.Role(
            self, 'CognitoDefaultUnauthenticatedRole',
            assumed_by=aws_iam.FederatedPrincipal(
                'cognito-identity.amazonaws.com',
                conditions={"StringEquals": {
                    "cognito-identity.amazonaws.com:aud": identity_pool.ref},
                    "ForAnyValue:StringLike": {
                        "cognito-identity.amazonaws.com:amr": "unauthenticated"}},
                assume_role_action="sts:AssumeRoleWithWebIdentity")
        )

        authenticated_role = aws_iam.Role(
            self, 'CognitoDefaultAuthenticatedRole',
            assumed_by=aws_iam.FederatedPrincipal(
                'cognito-identity.amazonaws.com',
                conditions={"StringEquals": {
                    "cognito-identity.amazonaws.com:aud": identity_pool.ref},
                    "ForAnyValue:StringLike": {"cognito-identity.amazonaws.com:amr": "authenticated"}},
                assume_role_action="sts:AssumeRoleWithWebIdentity")
        )

        authenticated_role.add_to_policy(aws_iam.PolicyStatement(
            effect=aws_iam.Effect.ALLOW,
            resources=["*"],
            actions=[
                "execute-api:Invoke",
                "execute-api:ManageConnections"
            ])
        )

        aws_cognito.CfnIdentityPoolRoleAttachment(
            self, "DefaultValid",
            identity_pool_id=identity_pool.ref,
            roles={
                "unauthenticated": unauthenticated_role.role_arn,
                "authenticated": authenticated_role.role_arn
            }
        )

        # endregion

        # region App
        repository = aws_codecommit.Repository(
            self, "mre-fan-experience-frontend",
            repository_name="mre-fan-experience-frontend"
        )

        app = aws_amplify.App(
            self, "app",
            app_name='mre-fan-experience-frontend',
            source_code_provider=aws_amplify.CodeCommitSourceCodeProvider(repository=repository)
        )

        app.add_branch('master')

        # endregion App

        core.CfnOutput(self, "webAppURL", value="master." + app.default_domain)
        core.CfnOutput(self, "webAppId", value=app.app_id)
        core.CfnOutput(self, "region", value=self.region)
        core.CfnOutput(self, "userPoolId", value=user_pool.user_pool_id)
        core.CfnOutput(self, "appClientId", value=user_pool_client.user_pool_client_id)
        core.CfnOutput(self, "identityPoolId", value=identity_pool.ref)


