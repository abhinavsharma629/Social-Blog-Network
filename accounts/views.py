from django.shortcuts import render,redirect ,HttpResponse,HttpResponseRedirect
from accounts.forms import EditProfileForm,UserCreationForm 
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserChangeForm,PasswordChangeForm
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.views.generic import TemplateView
from django.core.paginator import Paginator
from django.utils.html import format_html
from django.shortcuts import render,redirect
from django.contrib.auth.models import User
from accounts.forms import HomeForm
from accounts.models import Post
from google.cloud import translate
from django.http import HttpResponse
from django.db.models import Q
import os
from django.core.paginator import Paginator,EmptyPage, PageNotAnInteger
import speech_recognition as sr


os.environ["GOOGLE_APPLICATION_CREDENTIALS"]=os.getcwd()+"/translate.json"  #Getting language translation data from json file
translate_client = translate.Client()  # Setting up Client for Translation


#Registeration Of New User
def register(request):
    if request.method=="POST":
        form=UserCreationForm(request.POST)
        print("wait")
        if form.is_valid():
            print("yes")
			#update_session_auth_hash(request,form.user)
            form.save()
        return redirect('/account')
    else:
        form=UserCreationForm()
    args={'form':form}
    return render(request,'accounts/register1.html',args) #Changed name from reg_html to register1


#View You Profile
def view_profile(request):
    posts_list=Post.objects.all().order_by('-created')
    post_list = posts_list.filter(user=request.user)
    args = {'user':request.user,'posts':post_list}
    return render(request,'accounts/profile.html',args)


#Edit Profile
def edit_profile(request):
    if request.method=="POST":
        form=EditProfileForm(request.POST,instance=request.user)
        if form.is_valid():
        	form.save()
        	return redirect('/account/profile')	
    else:
        form=EditProfileForm(instance=request.user)
        args={'form': form, 'user':request.user}
        return render(request,'accounts/edit_profile.html',args)


#Password Change  	
def change_password(request):
    if request.method=="POST":
        form=PasswordChangeForm(data=request.POST,user=request.user)
        if form.is_valid():
        	form.save()
        	return redirect('/account/profile')	
        else:
            return redirect('/account/change-password')	
    else:
        form=PasswordChangeForm(user=request.user)
        args={'form': form}
        return render(request,'accounts/change_password.html',args)


#Class based View
class HomeView(TemplateView):
    template_name='accounts/home.html'  # Template to be rendered

    #Get request
    def get(self,request):
        posts_list=Post.objects.all().order_by('-created')
        user=User.objects.all().order_by('-created')
        page = request.GET.get('page', 1)
        paginator = Paginator(posts_list, 5)
        try:
            posts = paginator.page(page)
        except PageNotAnInteger:
            posts = paginator.page(1)
        except EmptyPage:
            posts = paginator.page(paginator.num_pages)
        args={'posts':posts ,'users':user }
        return render(request,self.template_name,args)

    #Post request
    def post(self,request):
        text=request.POST.get('q')  # Get user input

        #For translation of text
        translated_description = translate_client.translate(text,target_language='hi')
        translated_post = translated_description['translatedText']

        print(text)
        #print(request.FILES['submissionFile'], request.FILES['videoFile'])
        #print(request.FILES['submission_file'])

        if('submissionFile' in request.FILES):
            obj,notif=Post.objects.get_or_create(post=text,translated_post=translated_post, user=request.user, postImg=request.FILES['submissionFile'])
            #print(request.FILES['submissionFile'])

        elif('videoFile' in request.FILES):
            obj,notif=Post.objects.get_or_create(post=text,translated_post=translated_post, user=request.user, postVid=request.FILES['videoFile'])

        else:
            obj,notif=Post.objects.get_or_create(post=text,translated_post=translated_post, user=request.user)
     
        if notif is True:
            obj.save()
        return HttpResponseRedirect('/')  


#Speech To Text Conversion Post
def STT(request):
    mic_name = "Speakers / Headphones (Realtek"

    #How often values are recorded 
    sample_rate = 48000

    #Chunk is like a buffer. It stores 2048 samples (bytes of data) 
    #here.  
    #it is advisable to use powers of 2 such as 1024 or 2048 
    chunk_size = 2048
    
    #Initialize the recognizer 
    r = sr.Recognizer() 
      
    #generate a list of all audio cards/microphones 
    mic_list = sr.Microphone.list_microphone_names() 
    device_id=0
    
    #the following loop aims to set the device ID of the mic that 
    #we specifically want to use to avoid ambiguity. 
    for i, microphone_name in enumerate(mic_list):
        if microphone_name == mic_name: 
            device_id = i
            #print(i)
      
    #use the microphone as source for input. Here, we also specify  
    #which device ID to specifically look for incase the microphone  
    #is not working, an error will pop up saying "device_id undefined" 
    with sr.Microphone(device_index = device_id, sample_rate = sample_rate,  
                            chunk_size = chunk_size) as source: 
        
        #wait for a second to let the recognizer adjust the  
        #energy threshold based on the surrounding noise level 
        r.adjust_for_ambient_noise(source) 
        print ("Say Something....")
        
        #listens for the user's input 
        audio = r.listen(source) 
              
        try: 
            text = r.recognize_google(audio) 
            print ("you said: " + text )
            translated_description = translate_client.translate(text,target_language='hi')
            translated_post = translated_description['translatedText']
            obj,notif=Post.objects.get_or_create(post=text, translated_post=translated_post ,user=request.user)
            if notif is True:
                obj.save()
          
        #error occurs when google could not understand what was said 
        except sr.UnknownValueError: 
            print("Google Speech Recognition could not understand audio") 
          
        except sr.RequestError as e: 
            print("Could not request results from Google Speech Recognition service; {0}".format(e))
    
    return HttpResponseRedirect('/')