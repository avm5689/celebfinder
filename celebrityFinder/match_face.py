import json
import boto3
import requests
import sys
#from imdb import IMDb
from argparse import ArgumentParser

#celebrities = IMDb()
out_encoding = sys.stdout.encoding or sys.getdefaultencoding()
sns_client = boto3.client("sns")

def getTopicArn(topic):
    topicArn = None
    topics = sns_client.list_topics()["Topics"]
    for t in topics:
        if topic in json.dumps(t):
            topicArn = t["TopicArn"]
        return topicArn

def getRekognitionClient():
    return boto3.client("rekognition")

def get_bytes(image_url):
    req_for_image = requests.get(image_url, stream=True)
    file_object_from_req = req_for_image.raw
    req_data_bytes = file_object_from_req.read()
    return req_data_bytes

def detect_face(client, file):
    face_detected = False

    # InvalidImageException will be raised if Rekognition does not support the given image type.
    try:
        image_bytes = get_bytes(file)
        response = client.detect_faces(Image={'Bytes': image_bytes})
    except Exception:
        response = None

    if (response is not None):
        if (not response['FaceDetails']):
            face_detected = False
        else:
            face_detected = True
    
    return face_detected, response

def findCelebrity(client, file):
    face_matches = False
    image_bytes = get_bytes(file)
    response = client.recognize_celebrities(Image={'Bytes': image_bytes})

    face_matches = True
    return face_matches, response

def pp_json(json_thing, sort=True, indents=4):
    if type(json_thing) is str:
        print(json.dumps(json.loads(json_thing), sort_keys=sort, indent=indents))
    else:
        print(json.dumps(json_thing, sort_keys=sort, indent=-indents))
    return None

def process(event, context):
    print("Event receives is as follows: ------------")
    print(json.dumps(event))
    print("------------------------------------------")

    sns_record = event['Records'][0]
    sns_message = sns_record['Sns']['Message']
    sns_message_json = json.loads(sns_message)
    #message = sns_message_json['body']['message']
    image_url = sns_message_json['image_url']
    #collection_name = sns_message_json['collection_name']
    received_from = sns_message_json['from_number']
    send_to = sns_message_json['to_number']
    message = "Sorry, we couldn't find a recognized face in the image you sent. Please try another one!"
    body = {}
    client = getRekognitionClient()
    isCelebrity = False
    match_face_result = False

    #First, find a face in the given image
    result = detect_face(client, image_url)

    #Second, if there is a face, match it with the AWS Rekognition library
    if (result):
        print("Face detected!")
        match_face_result, match_face_response = findCelebrity(client, image_url)
        print(match_face_response)
        name_of_person = match_face_response["CelebrityFaces"][0]["Name"]
        print(name_of_person)
        message = "I found the celebrity you're looking for, and I'm pretty sure it's {0}. (P.S: I'm still learning, so it's possible I got it wrong.)".format(name_of_person)
    
    body = {
        "Message": message,
        "From_number": received_from,
        "To_number": send_to,
        "Input": event
    }

    print("Body of message: ------------")
    print(json.dumps(body))
    print("-----------------------------")

    topicArn = getTopicArn("dispatch_response")
    payload = json.dumps({'default':json.dumps(body)})
    if __name__ != '__main__':
        publish_response = sns_client.publish(TopicArn=topicArn, Message=payload, MessageStructure='json')
        print("Publish Response: {}".format(json.dumps(publish_response)))
    else:
        print("If this is not a test, the following response will be published to SNS")
        print("----------------------------------------------------------------------")
        print(payload)
        print("----------------------------------------------------------------------")
    return body

def main():
    args = get_args()

    test_message = "{\"collection_name\": \""+args.collection+"\", \"from_number\": \"18007001234\", \"to_number\": \"18779991234\", \"image_url\": \""+args.image+"\"}"
    print ("Test message is: ", test_message)
    request = { "Records":
        [
            {   "Sns": {
                        "Message": test_message
                        }
            }
        ]
    }
    context = None
    pp_json(process(request, context))
    print("All done!")

if __name__ == '__main__':
    main()
