ZIP_NAME=lambda_function.zip
LAMBDA_NAME=hudsonmendes-imdb2tmdb-movies-download-lambda

rm -rf $
zip $ZIP_NAME __init__.py
zip $ZIP_NAME lambda_function.py
zip $ZIP_NAME -r imdb2tmdb
pip install -r requirements.txt --target ./package
cd package
zip -r9 ../$ZIP_NAME *
cd ..
aws lambda update-function-code --function-name $LAMBDA_NAME --zip-file fileb://$ZIP_NAME
rm -rf $ZIP_NAME