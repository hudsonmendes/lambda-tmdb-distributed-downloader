ZIP_NAME=lambda_function.zip
LAMBDA_NAME=hudsonmendes-imdb2tmdb-movies-download-lambda
echo "Installing Lambda Function"
echo "--------------------------"
echo " zip_name   : ${ZIP_NAME}"
echo " lambda_name: ${LAMBDA_NAME}"
echo "--------------------------"

echo " Adding lambda files..."
rm -rf $
zip $ZIP_NAME __init__.py
zip $ZIP_NAME lambda_function.py
zip $ZIP_NAME -r imdb2tmdb

echo " Installing dependencies into ./package"
pip install -r requirements.txt --target ./package
cd package

echo " Compressing dependencies into zip"
zip -r9 ../$ZIP_NAME *
cd ..

echo " Uploading lambda into AWS..."
aws lambda update-function-code --function-name $LAMBDA_NAME --zip-file fileb://$ZIP_NAME
rm -rf $ZIP_NAME