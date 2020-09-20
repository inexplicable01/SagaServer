import requests

# BASE = "http://fatpanda1985.pythonanywhere.com/"

BASE = "http://127.0.0.1:5000/"

# response = requests.get(BASE )
# print (response.text())

# # response = requests.get(BASE)
# # print (response.json())


#Upload File
# files = {'file' : open('LongVideo.mp4','rb')}
#
# r=requests.post(BASE+'UPLOADS', files=files)
# print(r.json())
#

#Get File
r=requests.get(BASE+'UPLOADS')
# print(r.content)

file = open('try.mp4', "wb")
file.write(r.content)
file.close()


#Delete File
# r=requests.delete(BASE+'UPLOADS')
# print(r.json())


# print(r.text)