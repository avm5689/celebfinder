# CelebFinder

CelebFinder is a serverless application built on Python2 & Python3 that matches celebrity faces detected in MMS photos. This project was originally built and inspired based off of open-source code available at [https://github.com/skarlekar/faces](https://github.com/skarlekar/faces).

# Application Overview
The CelebFinder application is event-driven, taking advantage of a user's SMS/MMS messages for the presentation tier, Twilio to bridge SMS and AWS API Gateway, and three AWS Lambda functions written in Python making use of AWS Rekognition and its built-in celebrity recognition library.

Typical usage involves a user snapping a picture of a celebrity using his/her phone camera and sends the image to a phone number hosted in Twilio. The user gets a response with the name of the celebrity matched from the AWS Rekognition platform.

The CelebFinder application consists of two services:
- Twilio Communication Service (built in Python2)
- Celebrity Finder Service (built in Python3)

The services are decoupled to allow for different presentation tiers in future iterations.

# Architecture Overview
1. User sends image to SMS number
2. Twilio Message Gateway receives the SMS message and sends HTTP GET request to AWS API Gateway endpoint.
3. Request is passed from API Gateway to an SNS topic to process the request.
4. SNS ProcessRequest passes an event to trigger the Lambda function for CelebrityFinder.
5. Lambda queries AWS Rekognition with the Image from MMS message.
6. If a face is detected, Rekognition queries the AWS built-in celebrity recognition database and returns name.
7. Results (in the form of a composed message JSON) are passed to twilioCommunicationService via SNS subscription.
8. TwilioCommunicationService triggers an SNS subscription to the corresponding Lambda function (send_message).
9. SendMessage communicates back to Twilio's Messaging Service to send out the resulting SMS message.

This serverless architecture means that the code is only run in response to events. Therefore, cost is only incurred when the service is actually being used.

# Components
The application consists of the following components:
1. Python
2. Twilio
3. AWS Lambda
4. AWS Rekognition

# Setup Instructions
The setup instructions are derived from https://github.com/skarlekar/faces](https://github.com/skarlekar/faces) setup process, albeit with different changes, since we're not using virtual environments. You have the option of doing this, but I used a dedicated machine just for development of this code, so virtualenvs weren't necessary.
## Installing Python
If you are on a Mac or Linux machine, you probably already have Python installed. On Windows you have to install Python. 

Regardless of your operating system, you are better off using a virtual environment for running Python. [Anaconda](https://www.continuum.io/downloads) or its terse version [Miniconda](https://conda.io/miniconda.html) is a Python virtual environment that allows you to manage various versions and environments of Python. The installers come with Python and the package manager *conda* with it. Follow the instructions [here](https://conda.io/docs/install/quick.html) to install Miniconda. For this project we will use Python 2.7.

### Install Git
Git is a popular code revision control system. To install Git for your respective operating system follow the instructions [here](https://git-scm.com/book/en/v2/Getting-Started-Installing-Git).

### Install *CelebFinder* 
To install CelebFinder from Git, follow the instructions below:

    $ git clone --recursive https://github.com/avm5689/celebfinder.git

#### Setup Twilio Environment Variables
Update the *setTwilio.sh* in the repository with your credentials from Twilio and setup your environment. Instructions on using *vi* is [here](https://www.howtoforge.com/faq/how-to-edit-files-on-the-command-line).

    $ cd celebFinder
    $ vi setTwilio.sh
    $ source ./setTwilio.sh    

#### Test Twilio Setup
To test your Twilio setup, run the Python program *sendmessage.py* under *twilioTester*. This program simply sends a message to your mobile number using your Twilio credentials. *Note: Make sure you are running this in Python2.*

    $ python twilioTester/sendmessage.py

If you receive a message with an image on your mobile, your Twilio is setup is working.

### Install node.js and Serverless framework
Serverless framework is a node.js application. To use Serverless framework and run the CelebritySleuth application you need to install node.js. Follow the [instructions](https://serverless.com/framework/docs/providers/aws/guide/installation/) from Serverless website to install both node.js and the Serverless framework. 

Ensure your Serverless framework is operational using the following:

    $ serverless --version

### Amazon AWS Setup
1. Sign into your AWS account or [sign-up](https://console.aws.amazon.com/console/home?region=us-east-1) for one.
2. Setup your AWS credentials by following the instructions from [here](https://serverless.com/framework/docs/providers/aws/guide/credentials/).

### Testing your Serverless Setup
Now that you have setup AWS, it is time to test your Serverless setup by creating a mock function using the Serverless framework.

Create a test directory. In the test directory, create a Lambda function from the default template as follows:

    $ mkdir sls-tester
    $ cd sls-tester
    $ sls create --template aws-python --name sls-test
    
This should create two files in the current directory:

> serverless.yml
> 
> handler.py

The *serverless.yml* declares a sample service and a function. The *handler.py*  returns a message stating that your function executed successfully. 

To deploy the function, simply type:

    $ sls deploy --verbose

This should deploy the function. The verbose option provides extra information.

To test your function, type:

    $ sls invoke --function hello

If you get the following message, your Serverless setup is working.

      WARNING: You are running v1.9.0. v1.10.0 will include the following breaking changes:
        - Some lifecycle events for the deploy plugin will move to a new package plugin. More info -> https://git.io/vy1zC
    
      You can opt-out from these warnings by setting the "SLS_IGNORE_WARNING=*" environment variable.
    
    {
        "body": "{\"input\": {}, \"message\": \"Go Serverless v1.0! Your function executed successfully!\"}",
        "statusCode": 200
    }


----------
### Twilio Communication Service
The Twilio Communication Service [twilioCommunicationService](https://github.com/avm5689/celebfinder/tree/master/twilioCommunicationService) bridges Twilio's SMS messaging service with the Face Recognition Service. When the user sends a message to his/her Twilio number, the message is intercepted by Twilio's Messaging service. The Twilio Messaging service will forward the SMS message contents to AWS API Gateway URL. The AWS API Gateway in turn will invoke the  Request Processor (*process_request*) Lambda function in the *twilioCommunicationService*.

The *TwilioCommunicationService* supports two functions:
1. The *processRequest* function validates incoming requests and sends a response synchronously if the message contains a proper request. It then invokes the *celebFinder* service asynchronously through SNS to process the command.
2. The *sendResponse* function composes a response from the celebFinder service and sends the response back to the number from where the request originated.

#### Deploy Twilio Communication Service
Assuming your local Serverless setup is complete and the test above to test your Serverless setup passes, follow the instructions below to deploy the *twilioCommunicationService* using the Serverless framework:

Set your Twilio credentials by running the shell script you updated earlier. 

    $ source ./setTwilio.sh

Windows users, use:

    $ setTwilio.cmd

Change directory to the twilioCommunicationService directory and deploy the service by running *sls deploy* as shown below:

    $ cd twilioCommunicationService
    $ sls deploy --verbose

Ensure there are no errors in the deployment process. You can also head on to your [AWS Console](https://console.aws.amazon.com/apigateway/home?region=us-east-1#/apis) and verify that the API Gateway has been created. You should see an API Gateway called *dev-twilioCommunication*. 

Also ensure the Lambda functions are created by verifying that the *twilioCommunication-dev-processRequest* and *twilioCommunication-dev-sendResponse* lambda functions is available in the [AWS Lambda console](https://console.aws.amazon.com/lambda/home?region=us-east-1#/functions?display=list).

Ensure your Twilio credentials are setup as environment variables by clicking on each of the Lambda functions and verifying that the *TWILIO_AUTH_TOKEN* and *TWILIO_ACCOUNT_SID* have been created with the correct values in the *Environment Variables* section in the *Code* tab.

#### Setup Twilio Messaging Service
Follow the instructions below to setup the Messaging Service in Twilio and associate your Twilio number to the Messaging Service:

1. In the Twilio website, login to your account and head to the [Messaging Services](https://www.twilio.com/console/sms/services)

2. Click on the **+** under Messaging Services with Copilot to add a new Messaging service.

3. Give a name to your service and click on *Create*. Let us say, *CelebritySleuth*.

4. Under *Properties* in the *USE CASE* drop-down, select *Chat Bot/Interactive 2-way*.

5. In the *Inbound Settings* section, ensure *PROCESS INBOUND MESSAGES* is checked.

6. Copy and paste the [AWS API Gateway URL](https://github.com/skarlekar/faces/blob/master/aws-api-gateway-screenshot.png) from your AWS console into the *REQUEST URL* field and add */process_request* to the end of the URL.  Your URL should resemble: https://netxnasdfda.execute-api.us-east-1.amazonaws.com/dev/process_request

7. Select HTTP GET in the drop-down next to the field.  

7. Leave rest of the fields to its default value and click *SAVE*.

8. Head to the [Numbers](https://www.twilio.com/console/phone-numbers/incoming) section in the Twilio console.

9. Click on the number assigned to you. This will take you to the section where you can configure what should happen when an SMS message is sent to your Phone Number.

10. Under the *Messaging* section, select *Messaging Service* under the *CONFIGURE WITH* drop-down.

11. In the *MESSAGING SERVICE*, select the Messaging service that created in steps 2-8 above and click *SAVE*.


----------

### CelebrityFinder Service
The CelebrityFinder Service ([celebrityFinder](https://github.com/avm5689/celebfinder/tree/master/celebrityFinder)) currently only one function: matchFace. This matches a face to an existing one located in the AWS Rekognition Celebrity Library.

#### Deploy Face Recognition Service
Change directory to the celebFinder directory and deploy the service by running *sls deploy* as shown below:

    $ cd celebrityFinder
    $ sls deploy --verbose

Ensure there are no errors in the deployment process. You can also head on to your [AWS Lambda Console](https://console.aws.amazon.com/lambda/home?region=us-east-1#/functions?display=list) and verify that the Lambda function *faceRecognition-dev-matchFace* has been created.


----------

### Testing the application
To test the application, test by sending an MMS message with a celebrity photo to your Twilio number:

Does it work? Are you getting a message back from yonder? If not why? Look at the CloudWatch logs for your processRequest Lambda function. What is the issue?

If you look carefully you will find that the Lambda functions do not have enough permissions to operate the SNS topic or AWS Rekognition resources.

#### Fixing twilioCommunicationService
Open the *serverless.yml* file in the *twilioCommunicationService* and uncomment the section *iamRoleStatements*, save and deploy the service again.

    $ cd twilioCommunicationService
    $ vi serverless.yml
    $ sls deploy --verbose

Repeat sending the image again.

This time, you should get a message saying that you will get a response back momentarily. 

    All good. You should receive your response momentarily!

You can wait till the cows come home, but you are not getting a response are you? 

This is because, you have to provide more permissions to the Lambda functions in the *celebrityFinder*.

#### Fixing CelebrityFinder
Open the *serverless.yml* file in the *celebrityFinder* and uncomment the section *iamRoleStatements*, save and deploy the service again.

    $ cd twilioCommunicationService
    $ vi serverless.yml
    $ sls deploy --verbose

That should have fixed it. Now send an image

You should not only get the following response:

    All good. You should receive your response momentarily!

You should also get a response!
