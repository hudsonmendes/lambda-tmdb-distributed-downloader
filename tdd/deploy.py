import os
import sys
import subprocess
import shutil
import zipfile
import json
import boto3
from config import Config


class Deploy:
    """
    Runs this system's deployment pipeline
    """

    def __init__(
            self,
            lambda_name,
            queue_name,
            datalake_bucket_name,
            package_folder='./package',
            zip_path='/tmp/lambda_function.zip',
            **kwargs):

        self.role_name = f'{lambda_name}-role'

        self.cleanup = DeployCleanup(
            zip_path=zip_path,
            package_folder=package_folder)

        self.steps = [
            self.cleanup,
            DeployLocalDependencies(package_folder=package_folder),
            DeployZipLambda(zip_path=zip_path, package_folder=package_folder),
            DeployAwsIamRole(lambda_name=lambda_name, role_name=self.role_name),
            DeployAwsSqsQueue(queue_name=queue_name),
            DeployAwsLambdaFunction(lambda_name=lambda_name, zip_path=zip_path, role_name=self.role_name),
            DeployAwsLambdaTrigger(lambda_name=lambda_name, queue_name=queue_name)]

    def deploy(self):
        """
        Runs the `steps` of the pipeline
        - Cleans local assets
        - Adds code to Zip file
        - Adds dependencies to Zip file
        - Creates the AWS IAM role
        - Creates the AWS SQS queue
        - Creates the AWS Lambda function
        - Attaches AWS components together
        - Upload the Zip file to our lambda function
        - Cleans the environment
        """
        try:
            for step in self.steps:
                step.call()
        finally:
            self.cleanup.call()


class DeployCleanup:
    """
    Deletes the zip and the local installation of packages that
    are copied to the root of the zip.
    """

    def __init__(self, zip_path: str, package_folder: str):
        self.zip_path = zip_path
        self.package_folder = package_folder

    def call(self):
        print('Deploy, cleaning up environment')
        self.drop_zip()
        self.drop_packages()

    def drop_zip(self):
        if os.path.isfile(self.zip_path):
            os.remove(self.zip_path)

    def drop_packages(self):
        if os.path.isdir(self.package_folder):
            shutil.rmtree(self.package_folder)


class DeployLocalDependencies:
    """
    Installs the packages into the ./{package_folder}, allowing us
    to copy them to the root of the zip, so that the lambda function
    has access to the dependencies that it needs to run.
    """

    def __init__(self, package_folder):
        self.package_folder = package_folder

    def call(self):
        print('Deploy, saving dependencies locally')
        subprocess.check_call([
            sys.executable,
            '-m',
            'pip',
            'install',
            '-q',
            '-r',
            'requirements.txt',
            '--target',
            self.package_folder])


class DeployZipLambda:
    """
    Zips the code files that are required by the lambda function
    and the lambda function.
    """

    def __init__(
            self,
            zip_path: str,
            package_folder: str,
            **kwargs):
        self.zip_path = zip_path
        self.package_folder = package_folder

    def call(self):
        print('Deploy, adding code to ZIP')
        base_folder = os.getcwd()
        with zipfile.ZipFile(self.zip_path, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            zip_file.write('lambda_function.py')
            zip_targets = self.get_source_target_files(base_folder=base_folder)
            for source_path, destination_path in zip_targets:
                zip_file.write(source_path, destination_path)

    def get_source_target_files(self, base_folder):
        zip_files = []
        zip_files.extend(DeployZipLambda.get_sources_targets(
            base_folder=base_folder,
            target_folder='tdd',
            file_predicate=lambda file: file.endswith('.py')))
        zip_files.extend(DeployZipLambda.get_sources_targets(
            base_folder=base_folder,
            target_folder=self.package_folder))
        return zip_files

    @staticmethod
    def get_sources_targets(base_folder, target_folder, file_predicate=None):
        if not file_predicate:
            def file_predicate(x): return True
        lib_code_folder = os.path.join(base_folder, target_folder)
        for root, _, files in os.walk(lib_code_folder):
            for file in files:
                if file_predicate(file):
                    source_path = os.path.join(root, file)
                    destination_path = source_path[len(base_folder) + 1:]
                    yield source_path, destination_path


class DeployAwsIamRole:
    """
    Ensures that we have a AWS IAM role to run the program.
    """

    def __init__(self, lambda_name, role_name):
        self.path_prefix = '/service-role/'
        self.role_name = role_name
        self.polcy_names = [
            'AmazonS3FullAccess',
            'service-role/AWSLambdaSQSQueueExecutionRole',
            'service-role/AWSLambdaBasicExecutionRole']

    def call(self):
        iam_role = self.ensure_role()
        self.attach_policies(iam_role)

    def ensure_role(self):
        if self.does_role_exist():
            return self.get_role()
        else:
            return self.create_role()

    def does_role_exist(self):
        iam = boto3.client('iam')
        roles = iam.list_roles(
            PathPrefix=self.path_prefix,
            MaxItems=1000)['Roles']
        roles = [r for r in roles if r['RoleName'] == self.role_name]
        return next(iter(roles), None) != None

    def get_role(self):
        iam = boto3.resource('iam')
        return iam.Role(self.role_name)

    def create_role(self):
        iam = boto3.resource('iam')
        policy_doc = {
            "Version": "2012-10-17",
            "Statement": [{
                "Effect": "Allow",
                "Principal": {"Service": "lambda.amazonaws.com"},
                "Action": "sts:AssumeRole"
            }]
        }
        iam.create_role(
            Path='/service-role/',
            RoleName=self.role_name,
            Description=f"Execution role for TMDB Distributed Downloader lambda function",
            MaxSessionDuration=3600,
            AssumeRolePolicyDocument=json.dumps(policy_doc))
        return self.get_role()

    def attach_policies(self, iam_role):
        for policy_name in self.polcy_names:
            policy_arn = f'arn:aws:iam::aws:policy/{policy_name}'
            iam_role.attach_policy(PolicyArn=policy_arn)


class DeployAwsSqsQueue:
    """
    Ensures that we have a queue for which we can send messages.
    """

    def __init__(self, queue_name: str):
        self.queue_name = queue_name

    def call(self):
        print(f"Deploy, ensure queue {self.queue_name}")
        if not self.does_queue_exist():
            self.create_queue()

    def does_queue_exist(self):
        try:
            sqs = boto3.resource('sqs')
            sqs.get_queue_by_name(QueueName=self.queue_name)
            return True
        except boto3.client('sqs').exceptions.QueueDoesNotExist:
            return False

    def create_queue(self):
        sqs = boto3.client('sqs')
        sqs.create_queue(
            QueueName=self.queue_name,
            Attributes={'VisibilityTimeout': '900'})


class DeployAwsLambdaFunction:
    """
    Ensure that we have the lambda that reads from the queue
    and process the download of the partition specified in the message
    """

    def __init__(self, lambda_name: str, zip_path: str, role_name: str):
        self.lambda_name = lambda_name
        self.zip_path = zip_path
        self.role_name = role_name
        self.config = Config()

    def call(self):
        print(f"Deploy, ensure lambda {self.lambda_name}")
        with open(self.zip_path, 'rb') as zip_file:
            zip_buffer = zip_file.read()
            if not self.does_lambda_exist():
                self.create_lambda(zip_buffer)
            else:
                self.update_lambda_code(zip_buffer)

    def does_lambda_exist(self):
        lbd = boto3.client('lambda')
        try:
            lbd.get_function(FunctionName=self.lambda_name)
            return True
        except lbd.exceptions.ResourceNotFoundException:
            return False

    def create_lambda(self, zip_buffer):
        iam = boto3.resource('iam')
        role = iam.Role(self.role_name)

        lbd = boto3.client('lambda')
        lbd.create_function(
            FunctionName=self.lambda_name,
            Runtime='python3.6',
            Role=role.arn,
            Handler='lambda_function.lambda_handler',
            Code={'ZipFile': zip_buffer },
            Description='Distribute download for TMDB movies using IMDB movie ids.',
            Timeout=900,
            MemorySize=256,
            Publish=True,
            Environment={'Variables': self.config.to_env()})

    def update_lambda_code(self, zip_buffer):
        lbd = boto3.client('lambda')
        lbd.update_function_code(
            FunctionName=self.lambda_name,
            ZipFile=zip_buffer)


class DeployAwsLambdaTrigger:
    """
    If not yet linked, links the SQSL as a trigger to the Lambda.
    """

    def __init__(self, queue_name: str, lambda_name: str):
        self.queue_name = queue_name
        self.lambda_name = lambda_name

    def call(self):
        print(f"Deploy, link lambda {self.lambda_name} to queue {self.queue_name}")
        sqs = boto3.resource('sqs')
        queue = sqs.get_queue_by_name(QueueName=self.queue_name)
        queue_arn = queue.attributes['QueueArn']

        lbd = boto3.client('lambda')
        try:
            lbd.create_event_source_mapping(
                EventSourceArn=queue_arn,
                FunctionName=self.lambda_name,
                Enabled=True,
                BatchSize=1)
        except lbd.exceptions.ResourceConflictException:
            pass # already exists
