import os
import sys
import subprocess
import shutil
import zipfile
import boto3


class Deploy:
    """
    Runs this system's deployment pipeline
    """

    def __init__(
            self,
            lambda_name,
            package_folder='./package',
            zip_path='/tmp/lambda_function.zip',
            **kwargs):
        self.lambda_name = lambda_name
        self.package_folder = package_folder
        self.zip_path = zip_path
        self.aws_lambda = boto3.client('lambda')

    def deploy(self):
        """
        Runs the pipeline:
        - Cleans local assets
        - Adds code to Zip file
        - Adds dependencies to Zip file
        - Upload the Zip file to our lambda function
        - Cleans the environment
        """
        self.cleanup()
        self.local_dependencies()
        with zipfile.ZipFile(self.zip_path, 'w') as zip_file:
            self.pack_code_into(zip_file)
            self.pack_dependencies_into(zip_file)
        self.upload_code_to_lambda()
        # self.cleanup()

    def cleanup(self):
        print('Deploy, cleaning up environment')
        if os.path.isfile(self.zip_path):
            os.remove(self.zip_path)
        if os.path.isdir(self.package_folder):
            shutil.rmtree(self.package_folder)

    def local_dependencies(self):
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

    def pack_code_into(self, zip_file):
        print('Deploy, adding code to ZIP')
        base_folder = os.getcwd()
        lib_code_folder = os.path.join(base_folder, 'tdd')
        zip_file.write('lambda_function.py')
        for root, _, files in os.walk(lib_code_folder):
            for file in files:
                if file.endswith('.py'):
                    source_path = os.path.join(root, file)
                    destination_path = source_path[len(base_folder) + 1:]
                    zip_file.write(source_path, destination_path)

    def pack_dependencies_into(self, zip_file):
        print('Deploy, adding dependencies to ZIP')
        base_folder = os.path.join(os.getcwd(), self.package_folder)
        for root, _, files in os.walk(base_folder):
            for file in files:
                source_path = os.path.join(root, file)
                destination_path = source_path[len(base_folder) + 1:]
                zip_file.write(source_path, destination_path)

    def upload_code_to_lambda(self):
        print('Deploy, uploading ZIP to lambda')
        self.aws_lambda.update_function_code(
            FunctionName=self.lambda_name,
            ZipFile=self.zip_path,
            Publish=True)
