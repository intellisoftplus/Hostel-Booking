#!/usr/bin/env python
#
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
import webapp2
from google.appengine.api import users
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext import db
from google.appengine.ext.webapp import template
from google.appengine.api import mail

import webapp2
import os
import logging
import csv
import random
import datetime



from google.appengine.api import rdbms
from google.appengine.ext import webapp
from google.appengine.ext import blobstore
from google.appengine.ext.webapp import blobstore_handlers
from google. appengine.ext import db
from google.appengine.api import mail
from google.appengine.ext.webapp import template
from datetime import datetime
from google.appengine.ext import ndb
from datetime import timedelta

import jinja2
import re
import webapp2


template_path = os.path.join(os.path.dirname(__file__)) 

jinja2_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_path))

template_env = jinja2.Environment(loader=jinja2.FileSystemLoader(os.getcwd()))


class MainHandler(webapp2.RequestHandler):
    def get(self):
        
        user = users.get_current_user()
        url = users.create_login_url(self.request.uri)
        url_linktext = 'Sign In'

        values = {
                    'url_linktext'  : url_linktext,
                    'user'  :   user,
                    'url'   :   url
                            }

        if user:
            url = users.create_logout_url(self.request.uri)
            url_linktext = 'Logout'

            values = {
                    'url_linktext'  : url_linktext,
                    'user'  :   user,
                    'url'   :   url
                            }

            self.response.write(template.render('welcome.html', values))
        else:
            self.response.write(template.render('index.html', values))



class Apply(webapp2.RequestHandler):
	#handles logging in and out
    def get(self):
        user = users.get_current_user()
        url = users.create_login_url(self.request.uri)
        url_linktext = 'Sign In'

        values = {
                        'url_linktext'  : url_linktext,
                        'user'  :   user,
                        'url'   :   url
                                }


        if user:
            url = users.create_logout_url(self.request.uri)
            url_linktext = 'Logout'

            #Check if user has pending requests                 

            q = db.Query(studentModel)
            q.filter("email", user.email())
            #q.filter("r_status", "pending")
            #q.filter("r_status", "approved")
            m = q.fetch(1)


            if m:
                values = {
                    'm' : m,
                    'url_linktext'  : url_linktext,
                    'user'  :   user,
                    'url'   :   url

                }
                self.response.write(template.render('error.html', values))           

            
            else:
                values = {
                        'url_linktext'	: url_linktext,
                        'user'	:	user,
                        'url'	:	url
                                }

                self.response.write(template.render('index.html', values))
        else:
            self.response.write(template.render('index.html', values))


    def post(self):

        url = users.create_logout_url(self.request.uri)
        url_linktext = 'Logout'

        user = users.get_current_user()
        
        g = self.request.get('gender')

        #Request code
        x = random.randint(1000,99999999) 
        
        #Suggesting a room for the request
        rooms = db.GqlQuery("SELECT * FROM hostelDB WHERE av_space > :1 AND rm_gender = :2", 0, g).get()

        if rooms is None:
            self.redirect('/error')
            
        else:
            #r_room = rooms.hostel
            h_code = rooms.h_code
            hostel = rooms.hostel

            #Updating the roomDB to reduce the number of spaces avaible
            record = db.get(db.Key.from_path('hostelDB',h_code))
            c = record.av_space
            c = c - 1
            record.av_space = c
            record.put()

            #this handles saving student info to the DB
            studentDetails = studentModel(
                r_code = "REQ"+str(x),
                key_name = "REQ"+str(x),
            	name = self.request.get('name'),
            	adm_no = self.request.get('adm_no'),
            	email = user.email(),
            	course = self.request.get('course'),
                gender = self.request.get('gender'),
                #r_room = r_room,
                h_code = h_code,
                hostel = hostel,
                r_status = "pending"
        	)
            studentDetails.put()
           #JS pop up that tells thje sudent that their details have been saved
           #Alternatively, a page redirect to another page

           #Send email to student with the details of the request
           #Send email to Louis for approval

            r_code = "REQ"+str(x)
            recipient_add = user.email()
            sender_add = "ian@intellisoftplus.com"  #change this to a local account once deployed
            subject = "Form Successfully Submitted - Reference Number is "+ r_code 
            body = (
                    "Dear "+user.nickname()+",\n\n"+

                    "Your application was successfully submitted and is now under review. \n\n"+

                    "Below is your booking reference number:\n"+
                    r_code +"\n\n" +

                    "The NEXT STEP: Visit the housing department with the following items:\n"+
                    "1.Your Reference Number\n"+
                    "2.Bank Slip as proof of paying your hostel application fee.\n\n"+

                    "You can later use this number to track the status of your hostel application by following this procedure:\n\n"+
                    "1.Visit hostel.university.ac.ke\n"+
                    "2.Login using your official Email Address i.e. kariuki@students.pu.ac.ke\n"+
                    "3.Click on Search\n"+
                    "4.Enter the Ref No above to check the status of your application\n\n"+

                    "Meanwhile, we shall keep you informed via email with a status of your application whether APPROVED or DECLINED. Please keep checking your email every so often as we will keep you posted using this address.\n\n"+
                    "Regards,\n\n"+
                    "Hostel Booking."

                                  
                    )
            mail.send_mail(sender_add, recipient_add, subject, body)
            self.redirect('/succesful')

class Succesful(webapp2.RequestHandler):

    def get(self):
        user = users.get_current_user()
        url = users.create_login_url(self.request.uri)
        url_linktext = 'Login'

        if user:
            url = users.create_logout_url(self.request.uri)
            url_linktext = 'Logout'

        values = {
            'url_linktext'  : url_linktext,
            'user'  :   user,
            'url'   :   url
        }

        self.response.write(template.render('success.html', values))

class Admin(webapp2.RequestHandler):
    #admin section of the app
    def get(self):
        user = users.get_current_user()
        url = users.create_login_url(self.request.uri)
        url_linktext = 'Login'

        values = {

                    'url_linktext'  : url_linktext,
                    'user'  :   user,
                    'url'   :   url
                    


        }
       

        if user:
            url = users.create_logout_url(self.request.uri)
            url_linktext = 'Logout'
            room_status = None
            #if users.is_current_user_admin(): #work in progress 
            #Fetch all students from the DB
            rows = db.GqlQuery("SELECT * FROM studentModel WHERE room = :1 ", room_status)


            values = {
                    'url_linktext'  : url_linktext,
                    'user'  :   user,
                    'url'   :   url,
                    'rows'  :   rows
                    }

            self.response.write(template.render('admin.html', values))

        self.response.write(template.render('index.html',values))

class Hostel(webapp2.RequestHandler):
    #hadnles adding new hostels to a new DB
    def get(self):
        user = users.get_current_user()
        url = users.create_login_url(self.request.uri)
        url_linktext = 'Login'
        values = {  'url_linktext'  : url_linktext,
                    'user'  :   user,
                    'url'   :   url }       

        if user:

            email = user.email()

            rows = db.GqlQuery("SELECT * FROM adminUsers WHERE u_email = :1 ", email).get()

            if rows is None:
                self.redirect('/restricted')
            else:
                url = users.create_logout_url(self.request.uri)
                url_linktext = 'Logout'
                #display all rooms available in hostel DB
                rows = db.GqlQuery("SELECT * FROM hostelDB")
                values = {

                    'url_linktext'  : url_linktext,
                        'user'  :   user,
                        'url'   :   url,
                        'rows'  :   rows

                }

                self.response.write(template.render('hostels.html',values))
        else:
            self.response.write(template.render('index.html',values))

    def post(self):
        #Adding new resources logic
        

        #generating a random code for the rooms
        x = random.randint(1000,999999)
        #h_code = "RM"+str(x)

        room_details = hostelDB(
            #room_no = self.request.get('room_no'),
            hostel = self.request.get('hostel'),
            capacity = self.request.get('capacity'),
            av_space = int(self.request.get('av_space')),
            rm_gender = self.request.get('gender'),
            key_name="RM"+str(x),
            h_code = "RM"+str(x)
            )
        room_details.put()
        self.redirect('/hostel')

class EditHostel(webapp2.RequestHandler):
    def get(self):
        user = users.get_current_user()
        url = users.create_login_url(self.request.uri)
        url_linktext = 'Login'
        values = {  'url_linktext'  : url_linktext,
                    'user'  :   user,
                    'url'   :   url }       

        if user:

            email = user.email()

            rows = db.GqlQuery("SELECT * FROM adminUsers WHERE u_email = :1 ", email).get()

            if rows is None:
                self.redirect('/restricted')
            else:
                url = users.create_logout_url(self.request.uri)
                url_linktext = 'Logout'
                #display all rooms available in hostel DB
                rows = db.GqlQuery("SELECT * FROM hostelDB")
                values = {

                    'url_linktext'  : url_linktext,
                        'user'  :   user,
                        'url'   :   url,
                        'rows'  :   rows

                }

                self.response.write(template.render('edit_hostel.html',values))
        else:
            self.response.write(template.render('index.html',values))
    def post(self):

        h_id = self.request.get('h_id')
        hostel = self.request.get('hostel')
        capacity = self.request.get('capacity')
        space = self.request.get('av_space')
        gender = self.request.get('rm_gender')

        record = db.get(db.Key.from_path('hostelDB', h_id))
        #record.h_code = h_id
        record.hostel = hostel
        record.capacity = capacity
        record.av_space = int(space)
        record.rm_gender = gender
        record.put()

        self.redirect('/editHostel')
    
        #h_id = self.request.get('id')
        #record = db.get(db.Key.from_path('hostelDB', h_id))
        #record.delete()
        #self.redirect('/editHostel')
class DeleteHostel(webapp2.RequestHandler):
    def get(self, h_id):

        user = users.get_current_user()
        
        record = db.get(db.Key.from_path('hostelDB', h_id))
        db.delete(record)

        rows = db.GqlQuery("SELECT * FROM hostelDB")

        values = {
            'user'  : user,
            'rows'  : rows

        }

        self.redirect('/editHostel')
        #self.redirect('/hostel')


class Search(webapp2.RequestHandler):
    #this class handles searching for requests
    def get(self):
        user = users.get_current_user()
        url = users.create_login_url(self.request.uri)
        url_linktext = 'Login'
        values = {  'url_linktext'  : url_linktext,
                    'user'  :   user,
                    'url'   :   url }    
        

        if user:
            email = user.email()

            rows = db.GqlQuery("SELECT * FROM adminUsers WHERE u_email = :1 ", email).get()

            if rows is None:
                self.redirect('/restricted')

            else:
                url = users.create_logout_url(self.request.uri)
                url_linktext = 'Logout'
                values = {

                        'url_linktext'  : url_linktext,
                        'user'  :   user,
                        'url'   :   url,
                }
                self.response.write(template.render('search.html',values))
        else:
            self.response.write(template.render('index.html',values))

    def post(self):
        user = users.get_current_user()
        r_code = self.request.get('r_code')
        url = users.create_logout_url(self.request.uri)
        url_linktext = 'Logout'

        rows = db.GqlQuery("SELECT * FROM studentModel WHERE r_code = :1", r_code)
        values = {

            'rows' :  rows
            

        }
        #this method makes the r_code& h_code that was last returned available globally
        global req_no, rm_code
       
        for row in rows:
            req_no = row.r_code
            rm_code = row.h_code
        ######################################################################

        self.response.write(template.render('search.html',values))

class SearchRequests(webapp2.RequestHandler):
    def get(self):
        user = users.get_current_user()
        url = users.create_login_url(self.request.uri)
        url_linktext = 'Login'
        values = {  'url_linktext'  : url_linktext,
                    'user'  :   user,
                    'url'   :   url }    
        

        if user:        
            
            url = users.create_logout_url(self.request.uri)
            url_linktext = 'Logout'
            values = {

                    'url_linktext'  : url_linktext,
                    'user'  :   user,
                    'url'   :   url,
            }
            self.response.write(template.render('search_request.html',values))
        else:
            self.response.write(template.render('index.html',values))

    def post(self):
        user = users.get_current_user()
        r_code = self.request.get('r_code')
        url = users.create_logout_url(self.request.uri)
        url_linktext = 'Logout'

        #rows = db.GqlQuery("SELECT * FROM studentModel WHERE r_code = :1", r_code)
        query = db.Query(studentModel)
        query.filter("r_code =", r_code)
        rows = query.fetch(1)

        if rows:
            for row in rows:
                r = row.r_status
            #r = rows.r_status

            if r == "approved":
                message = "Your request was approved. Kindly check your email address for futher details."
            else:
                message = "Your request is still under review, check your email address for futher details."
            values = {

                'rows' :  rows,
                'user' : user,
                'url' : url,
                'url_linktext' : url_linktext,
                'message'  : message
                

            }
            self.response.write(template.render('search_request.html',values))            
        else:
            message_e = "We can't find your Reference Number."
            values = {               
                'user' : user,
                'url' : url,
                'url_linktext' : url_linktext,
                'message_e' :   message_e              
                

            }
            
            self.response.write(template.render('search_request.html',values)) 



class Approve(webapp2.RequestHandler):
    def get(self, r_code):
        
        #this class updates the request status to approved
        user = users.get_current_user()
        record = db.get(db.Key.from_path('studentModel', r_code))
        record.r_status = "approved"
        record.put()

        #Write Email to student letting them know that their request has been approved and accomodation details
        recipient_add = record.email #change this to a local account once deployed
        sender_add = user.email()
        
        subject = "Congratulations - Your Application was APPROVED." 
        body = (
                "Congratulations "+record.name+",\n\n"+
                "You have now been allocated a room in hostel "+record.hostel+"\n"+
                
                "Please visit the housing department to collect your Keys.\n"+
                "Enjoy the rest of your stay and studies at Pwani University.\n \n"+
                "Regards,\n \n"+
                "Hostel Booking"

                )
        mail.send_mail(sender_add, recipient_add, subject, body)

        self.redirect('/search') # redirect to approved succesful page

class Decline(webapp2.RequestHandler):
    def get(self, r_code):
        user = users.get_current_user()

        url = users.create_logout_url(self.request.uri)
        url_linktext = 'Logout'

        #Confirm that the Status is not Approved
        q = db.Query(studentModel)
        q.filter("r_code",r_code )
        q.filter("r_status", "approved")            
        m = q.fetch(1)

        if m:
            self.redirect('/approvalerror')
 
        else:        
            #mark the request as rejected
            record = db.get(db.Key.from_path('studentModel', r_code))
            h = record.h_code
            db.delete(record)

            #Update the hostelDB av_spaces + 1
            spaces = db.get(db.Key.from_path('hostelDB', h))
            r = spaces.av_space
            r = r + 1
            spaces.av_space = r
            spaces.put()

            #Write an email to the user telling them that their request was rejected and
            #they should try again
             #Write Email to student letting them know that their request has been approved and accomodation details
            recipient_add = record.email #change this to a local account once deployed
            sender_add = user.email() 
            
            subject = "Sorry - Your Application was DECLINED" 
            body = (
                    "Dear "+record.name+",\n\n"+
                    "Your room allocation request "+ record.r_code+" has been declined.\n"+
                    "You can attempt to apply again here: http://isphostelapp.appspot.com/ \n \n"+
                    "Apologies for any inconvenience caused.\n \n"+
                    "Regards, \n \n"+
                    "Hostel Booking"                           
                    )
            mail.send_mail(sender_add, recipient_add, subject, body)
            self.redirect('/search')

class RequestTimer(webapp2.RequestHandler):
    def get(self):

        date_c = datetime.now()

        #Suspending ticket
        #qry = studentModel.query(date_c - studentModel.date  >= 3 )
        qry =db.GqlQuery("SELECT * FROM studentModel WHERE r_status = :1", "pending")
        for q in qry:
            m = q.r_code
            d = q.date

            if (date_c - d) >= timedelta(days=3):
                r = db.get(db.Key.from_path('studentModel', m))
                r.r_status = "suspended"
                r.put()
                #send email explaining to student COMING SOON
                recipient_add = record.email #change this to a local account once deployed
                sender_add = "ian@intellisoftplus.com" #Change this during deployment
                
                subject = "Room Allocation Request Suspended" 
                body = (
                        "Dear "+r.name+",\n\n"+
                        "This is to inform you that your room allocation request "+ r.r_code+" has been suspended and will be automatically deleted in 3 days."+
                        "Kindly visit the housing department for assistance."               
                        )
                mail.send_mail(sender_add, recipient_add, subject, body)

        #Declining Ticket
        qry2 =db.GqlQuery("SELECT * FROM studentModel WHERE date = :1", "suspended")
        for q in qry2:
            m = q.r_code
            n = q.h_code
            d = q.date

            if (date_c - d) >= timedelta(days=6):
                record = db.get(db.Key.from_path('studentModel', m))
                db.delete(record)

                #Update the hostelDB av_spaces + 1
                spaces = db.get(db.Key.from_path('hostelDB', n))
                r = spaces.av_space
                r = r + 1
                spaces.av_space = r
                spaces.put()

                #Write an email to the user telling them that their request was rejected and
                #they should try again
                recipient_add = record.email #change this to a local account once deployed
                sender_add = "ian@intellisoftplus.com" 
                
                subject = "Sorry - Your Application was DECLINED" 
                body = (
                        "Dear "+record.name+",\n\n"+
                        "Your application "+record.r_code+" was DECLINED due to the following reason:\n \n " 
                        "Kindly visit the Hostel Allocation portal and try again."           
                        )
                mail.send_mail(sender_add, recipient_add, subject, body)  
class AdminUsers(webapp2.RequestHandler):
    #this is a security class, it enables super admin to add admin users to the app
    def get(self):
        user = users.get_current_user()
        url = users.create_login_url(self.request.uri)
        url_linktext = 'Login'
        values = {  'url_linktext'  : url_linktext,
                    'user'  :   user,
                    'url'   :   url }  
       

        if user:
            email = user.email()

            rows = db.GqlQuery("SELECT * FROM adminUsers WHERE u_email = :1 ", email).get()

            if rows is None:
                self.redirect('/restricted')
            else:
                url = users.create_logout_url(self.request.uri)
                url_linktext = 'Logout'
                #display admin users
                rows = db.GqlQuery("SELECT * FROM adminUsers")
                values = {

                    'url_linktext'  : url_linktext,
                        'user'  :   user,
                        'url'   :   url,
                        'rows'  :   rows

                }

                self.response.write(template.render('users.html',values))
        else:
            self.response.write(template.render('index.html', values))
    def post(self):
        #Adding new admin users
        #generating a random code for the users
        x = random.randint(1000,999999)       

        admin_details = adminUsers(
            u_name = self.request.get('u_name'),
            u_email = self.request.get('u_email'),
            u_dept = self.request.get('u_dept'),
            key_name="USR"+str(x),
            u_code = "USR"+str(x)
            )
        admin_details.put()
        self.redirect('/succesful')

class Restricted(webapp2.RequestHandler):
    def get(self):


        user = users.get_current_user()
        url = users.create_login_url(self.request.uri)
        url_linktext = 'Login'
        values = {

                            'url_linktext'  : url_linktext,
                                'user'  :   user,
                                'url'   :   url}



        if user:
            url = users.create_logout_url(self.request.uri)
            url_linktext = 'Logout'
            values = {

                    'url_linktext'  : url_linktext,
                        'user'  :   user,
                        'url'   :   url
                       

                }

            self.response.write(template.render('restricted.html',values))
        else:
            self.response.write(template.render('index.html', values))
class ErrorHandler(webapp2.RequestHandler):
    def get(self):
        user = users.get_current_user()
        url = users.create_login_url(self.request.uri)
        url_linktext = 'Login'

        if user:
            url = users.create_logout_url(self.request.uri)
            url_linktext = 'Logout'

        values = {
                'url_linktext'  : url_linktext,
                'user'  :   user,
                'url'   :   url
                        }

        self.response.write(template.render('error.html', values))

class ApprovalError(webapp2.RequestHandler):
    def get(self):
        user = users.get_current_user()
        url = users.create_login_url(self.request.uri)
        url_linktext = 'Login'

        if user:
            url = users.create_logout_url(self.request.uri)
            url_linktext = 'Logout'

        values = {
                'url_linktext'  : url_linktext,
                'user'  :   user,
                'url'   :   url
                        }

        self.response.write(template.render('approvalerror.html', values))
class StudentHelp(webapp2.RequestHandler):
    def get(self):
        user = users.get_current_user()
        url = users.create_login_url(self.request.uri)
        url_linktext = 'Login'

        if user:
            url = users.create_logout_url(self.request.uri)
            url_linktext = 'Logout'
            values = {
                'url_linktext'  : url_linktext,
                'user'  :   user,
                'url'   :   url
                        }
            
        self.response.write(template.render('student_help.html', values))         





class hostelDB(db.Model):
    h_code = db.StringProperty()#key_name
    #room_no = db.StringProperty()
    hostel = db.StringProperty()
    capacity = db.StringProperty()
    av_space = db.IntegerProperty()#convert this to int when updating it then
    rm_gender = db.StringProperty() 


class studentModel(db.Model):
    r_code = db.StringProperty() #key_name
    name = db.StringProperty()
    adm_no = db.StringProperty()
    gender = db.StringProperty()
    email = db.StringProperty()
    course = db.StringProperty()
    date = db.DateTimeProperty(auto_now_add=True)
    #r_room = db.StringProperty()#Auto filled
    hostel = db.StringProperty()
    h_code = db.StringProperty()#Auto filled
    r_status  = db.StringProperty()

class adminUsers(db.Model):
    u_code = db.StringProperty()#key_name
    u_name = db.StringProperty()
    u_email = db.StringProperty()
    u_dept = db.StringProperty()
    u_date = db.DateTimeProperty(auto_now_add=True)


app = webapp2.WSGIApplication([
    ('/', MainHandler),
    ('/apply', Apply),    
    ('/succesful', Succesful),
    #('/admin', Admin),
    ('/hostel', Hostel),
    ('/search',Search),
    ('/approve/([-\w]+)', Approve),
    ('/decline/([-\w]+)', Decline),
    ('/help', StudentHelp),
    ('/reqesttimer', RequestTimer),
    ('/users', AdminUsers),
    ('/restricted', Restricted),
    ('/error', ErrorHandler),
    ('/editHostel', EditHostel),
    ('/search_request', SearchRequests),
    ('/deletehostel/([-\w]+)', DeleteHostel),
    ('/approvalerror', ApprovalError)
   
], debug=True)
