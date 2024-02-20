
from django.http import JsonResponse
from django.shortcuts import render, redirect
from .models import *
from django.contrib import messages
from django.contrib.auth.models import User, auth
from django.utils.crypto import get_random_string
import random
from django.conf import settings
from django.core.mail import send_mail
from django.utils import timezone
from .models import Company
from django.shortcuts import render, redirect
from django.http import JsonResponse


from django.core.mail import send_mail, EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from io import BytesIO
from xhtml2pdf import pisa
from django.http.response import JsonResponse, HttpResponse


def home(request):
  return render(request, 'home.html')

def login(request):
  return render(request, 'login.html')

def forgot_password(request):
  return render(request, 'forgot_password.html')

def cmp_register(request):
  return render(request, 'cmp_register.html')

def cmp_details(request,id):
  context = {'id':id}
  return render(request, 'cmp_details.html', context)

def emp_register(request):
  return render(request, 'emp_register.html')

def register_company(request):
  if request.method == 'POST':
    fname = request.POST['fname']
    lname = request.POST['lname']
    email = request.POST['email']
    uname = request.POST['uname']
    phno = request.POST['phno']
    passw = request.POST['pass']
    cpass = request.POST['cpass']
    rfile = request.FILES.get('rfile')

    if passw == cpass:
      if CustomUser.objects.filter(username = uname).exists():
        messages.info(request, 'Sorry, Username already exists !!')
        return redirect('cmp_register')

      elif not CustomUser.objects.filter(email = email).exists():
        user_data = CustomUser.objects.create_user(first_name = fname, last_name = lname, username = uname, email = email, password = passw, is_company = 1)
        cmp = Company( contact = phno, user = user_data, profile_pic = rfile)
        cmp.save()
        return redirect('cmp_details',user_data.id)

      else:
        messages.info(request, 'Sorry, Email already exists !!')
        return redirect('cmp_register')
      
    messages.info(request, 'Sorry, Passwords must match !!')
    return render(request,'cmp_register.html')
  
def register_company_details(request,id):
  if request.method == 'POST':
    cname = request.POST['cname']
    address = request.POST['address']
    city = request.POST['city']
    state = request.POST['state']
    country = request.POST['country']
    pincode = request.POST['pincode']
    pannumber = request.POST['pannumber']
    gsttype = request.POST['gsttype']
    gstno = request.POST['gstno']

    code=get_random_string(length=6)

    usr = CustomUser.objects.get(id = id)
    cust = Company.objects.get(user = usr)
    cust.company_name = cname
    cust.address = address
    cust.city = city
    cust.state = state
    cust.company_code = code
    cust.country = country
    cust.pincode = pincode
    cust.pan_number = pannumber
    cust.gst_type = gsttype
    cust.gst_no = gstno
    cust.save()
    return redirect('login')

def register_employee(request):
  if request.method == 'POST':
    fname = request.POST['fname']
    lname = request.POST['lname']
    email = request.POST['email']
    uname = request.POST['uname']
    phno = request.POST['phno']
    passw = request.POST['pass']
    cpass = request.POST['cpass']
    ccode = request.POST['ccode']
    rfile = request.FILES.get('rfile')

    if not Company.objects.filter(company_code = ccode).exists():
      messages.info(request, 'Sorry, Company Code is Invalid !!')
      return redirect('emp_register')
    
    cmp = Company.objects.get(company_code = ccode)
    emp_names = Employee.objects.filter(company = cmp).values_list('user',flat=True)
    for e in emp_names:
       usr = CustomUser.objects.get(id=e)
       if str(fname).lower() == (usr.first_name ).lower() and str(lname).lower() == (usr.last_name).lower():
        messages.info(request, 'Sorry, Employee With this name already exits, try adding an initial !!')
        return redirect('emp_register')
    
    if passw == cpass:
      if CustomUser.objects.filter(username = uname).exists():
        messages.info(request, 'Sorry, Username already exists !!')
        return redirect('emp_register')

      elif not CustomUser.objects.filter(email = email).exists():
        user_data = CustomUser.objects.create_user(first_name = fname, last_name = lname, username = uname, email = email, password = passw)
        emp = Employee(user = user_data, company = cmp, profile_pic = rfile, contact=phno)
        emp.save()
        return redirect('login')

      else:
        messages.info(request, 'Sorry, Email already exists !!')
        return redirect('emp_register')
      
    messages.info(request, 'Sorry, Passwords must match !!')
    return render(request,'emp_register.html')
  
def change_password(request):
  if request.method == 'POST':
    email= request.POST.get('email')
    if not CustomUser.objects.filter(email=email).exists():
      messages.success(request,'No user found with this email !!')
      return redirect('forgot_password')
    
    else:
      otp = random.randint(100000, 999999)
      usr = CustomUser.objects.get(email=email)
      usr.set_password(str(otp))
      usr.save()

      subject = 'Password Reset Mail'
      message = f'Hi {usr.first_name} {usr.last_name}, Your Otp for password reset is {otp}'
      email_from = settings.EMAIL_HOST_USER
      recipient_list = [email ]
      send_mail(subject, message, email_from, recipient_list)
      messages.info(request,'Password reset mail sent !!')
      return redirect('forgot_password')

def user_login(request):
  if request.method == 'POST':
    email = request.POST['email']
    cpass = request.POST['pass']

    try:
      usr = CustomUser.objects.get(email=email)
      log_user = auth.authenticate(username = usr.username, password = cpass)
      if log_user is not None:
        if usr.is_company == 1:
          auth.login(request, log_user)
          return redirect('dashboard')
        else:
          emp = Employee.objects.get(user=usr)
          if emp.is_approved == 0:
            messages.info(request,'Employee is not Approved !!')
            return redirect('login')
          else:
            auth.login(request, log_user)
            return redirect('dashboard')
      messages.info(request,'Invalid Login Details !!')
      return redirect('login')
    
    except:
        messages.info(request,'Employee do not exist !!')
        return redirect('login')
    

def dashboard(request):
  context = {'usr':request.user}
  return render(request, 'dashboard.html', context)

def logout(request):
  auth.logout(request)
  return redirect('/')

def cmp_profile(request):
  cmp = Company.objects.get(user = request.user)
  context = {'usr':request.user, 'cmp':cmp}
  return render(request,'cmp_profile.html',context)

def load_edit_cmp_profile(request):
  cmp = Company.objects.get(user = request.user)
  context = {'usr':request.user, 'cmp':cmp}
  return render(request,'cmp_profile_edit.html',context)

def edit_cmp_profile(request):
  cmp =  Company.objects.get(user = request.user)
  if request.method == 'POST':
    email = request.POST['email']
    current_email = cmp.user.email
    if email != current_email:
      if CustomUser.objects.filter(email=email).exists():
        messages.info(request,'Email Already in Use')
        return redirect('load_edit_cmp_profile')

    cmp.company_name = request.POST['cname']
    cmp.user.email = request.POST['email']
    cmp.user.first_name = request.POST['fname']
    cmp.user.last_name = request.POST['lname']
    cmp.contact = request.POST['phno']
    cmp.address = request.POST['address']
    cmp.city = request.POST['city']
    cmp.state = request.POST['state']
    cmp.country = request.POST['country']
    cmp.pincode = request.POST['pincode']
    cmp.pan_number = request.POST['pan']
    cmp.gst_type = request.POST['gsttype']
    cmp.gst_no = request.POST['gstnoval']
    old=cmp.profile_pic
    new=request.FILES.get('image')
    if old!=None and new==None:
      cmp.profile_pic=old
    else:
      cmp.profile_pic=new
    
    cmp.save() 
    cmp.user.save() 
    return redirect('cmp_profile') 
  
def emp_profile(request):
  emp = Employee.objects.get(user=request.user)
  context = {'usr':request.user, 'emp':emp}
  return render(request,'emp_profile.html',context)

def load_edit_emp_profile(request):
  emp = Employee.objects.get(user=request.user)
  context = {'usr':request.user, 'emp':emp}
  return render(request,'emp_profile_edit.html',context)

def edit_emp_profile(request):
  emp =  Employee.objects.get(user = request.user)
  if request.method == 'POST':
    email = request.POST['email']
    current_email = emp.user.email
    if email != current_email:
      if CustomUser.objects.filter(email=email).exists():
        messages.info(request,'Email Already in Use')
        return redirect('load_edit_emp_profile')

    emp.user.email = request.POST['email']
    emp.user.first_name = request.POST['fname']
    emp.user.last_name = request.POST['lname']
    emp.contact = request.POST['phno']
    old=emp.profile_pic
    new=request.FILES.get('image')
    if old!=None and new==None:
      emp.profile_pic=old
    else:
      emp.profile_pic=new
    
    emp.save() 
    emp.user.save() 
    return redirect('emp_profile') 

def load_staff_request(request):
  cmp = Company.objects.get(user = request.user)
  emp = Employee.objects.filter(company = cmp, is_approved = 0)
  context = {'usr':request.user, 'emp':emp, 'cmp':cmp}
  return render(request,'staff_request.html',context)

def load_staff_list(request):
  cmp = Company.objects.get(user = request.user)
  emp = Employee.objects.filter(company = cmp, is_approved = 1)
  context = {'usr':request.user, 'emp':emp, 'cmp':cmp}
  return render(request,'staff_list.html',context)

def accept_staff(request,id):
  emp = Employee.objects.get(id=id)
  emp.is_approved = 1
  emp.save()
  messages.info(request,'Employee Approved !!')
  return redirect('load_staff_request')

def reject_staff(request,id):
  Employee.objects.get(id=id).delete()
  messages.info(request,'Employee Deleted !!')
  return redirect('load_staff_request')

def item_list(request):
  if request.user.is_company:
    itm = Item.objects.filter(company = request.user.company)
  else:
    itm = Item.objects.filter(company = request.user.employee.company)
  
  if itm:
    fitm = itm[0]
    ftrans = Transactions.objects.filter(item = fitm)
    context = {'itm':itm, 'usr':request.user, 'fitm':fitm, 'ftrans':ftrans}
  else:
        context = {'itm':itm, 'usr':request.user}
  return render(request,'item_list.html',context)

def load_item_create(request):
  tod = timezone.now().date().strftime("%Y-%m-%d")
  return render(request,'item_create.html',{'tod':tod, 'usr':request.user})

def item_create(request):
  if request.method=='POST':
    itm_type = request.POST.get('itm_type')
    if itm_type:
      type = 'Service'
    else:
      type = 'Goods'
    itm_name = request.POST.get('name')
    itm_hsn = request.POST.get('hsn')
    itm_unit = request.POST.get('unit')
    itm_vat = request.POST.get('vat')
    taxable_result = request.POST.get('taxable_result')
    itm_sale_price = request.POST.get('sale_price')
    itm_purchase_price = request.POST.get('purchase_price')
    stock_in_hand = request.POST.get('stock_in_hand')
    if stock_in_hand == '' or None :
      stock_in_hand = 0
    itm_at_price = request.POST.get('at_price')
    if itm_at_price == '' or None:
      itm_at_price = 0
    itm_date = request.POST.get('itm_date')
    
    item = Item(user = request.user,
                itm_type = type,
                itm_name = itm_name,
                itm_hsn = itm_hsn,
                itm_unit = itm_unit,
                itm_vat = itm_vat,
                itm_taxable = taxable_result,
                itm_sale_price = itm_sale_price,
                itm_purchase_price = itm_purchase_price,
                itm_stock_in_hand = stock_in_hand,
                itm_at_price = itm_at_price,
                itm_date = itm_date)
    item.save()

    trans = Transactions(user = request.user, item = item, trans_type = 'Stock Open', trans_date = itm_date, trans_qty = 0, trans_current_qty = stock_in_hand, 
                         trans_adjusted_qty = stock_in_hand, trans_price = itm_at_price)

    if request.user.is_company:
      item.company = request.user.company
      trans.company = request.user.company

    else:
      item.company = request.user.employee.company
      trans.company = request.user.employee.company
 
    item.save()
    trans.save()

    if request.POST.get('save_and_next'):
      return redirect('load_item_create')
    elif request.POST.get('save'):
      return redirect('item_list')
    





def party_list(request):
  if request.user.is_company:
    party = Party.objects.filter(company = request.user.company)
  else:
    party = Party.objects.filter(company = request.user.employee.company)
  
  if party:
    fparty = party[0]
    ftrans = Transactions_party.objects.filter(party = fparty)
    context = {'party':party, 'usr':request.user, 'fparty':fparty, 'ftrans':ftrans}
  else:
        context = {'party':party, 'usr':request.user}
  return render(request,'parties_list.html',context)


def load_party_create(request):
  tod = timezone.now().date().strftime("%Y-%m-%d")
  return render(request,'add_parties.html',{'tod':tod, 'usr':request.user})

from django.db import IntegrityError
from django.shortcuts import render, redirect

def addNewParty(request):
    if request.user.is_company:
        cmp = request.user.company
    else:
        cmp = request.user.employee.company

    error_message = None  # Initialize error message

    if request.method == 'POST':
        party_name = request.POST['partyname']
        trn_no = request.POST['trn_no']
        contact = request.POST['contact']
        trn_type = request.POST['trn_type']
        state = request.POST.get('state')
        address = request.POST['address']
        email = request.POST['email']
        openingbalance = request.POST.get('balance', '')
        payment = request.POST.get('paymentType', '')
        current_date = request.POST['currentdate']
        End_date = request.POST.get('enddate', None)
        additionalfield1 = request.POST['additionalfield1']
        additionalfield2 = request.POST['additionalfield2']
        additionalfield3 = request.POST['additionalfield3']

        try:
            # Check if a party with the same trn_no already exists
            if Party.objects.filter(trn_no=trn_no, company=cmp).exists():
                error_message = 'An error occurred while processing your request. TRN number already exists. Please enter a unique TRN number.'
            # Check if a party with the same email already exists
            elif Party.objects.filter(email=email, company=cmp).exists():
                error_message = 'An error occurred while processing your request. Email already exists. Please enter a unique email address.'
            else:
                part = Party(party_name=party_name, trn_no=trn_no, contact=contact, trn_type=trn_type, state=state,
                             address=address, email=email, openingbalance=openingbalance, payment=payment,
                             current_date=current_date, End_date=End_date, additionalfield1=additionalfield1,
                             additionalfield2=additionalfield2, additionalfield3=additionalfield3)

                if request.user.is_company:
                    part.company = request.user.company
                else:
                    part.company = request.user.employee.company

                part.save()

                trans = Transactions_party(user=request.user, trans_type='Opening Balance', trans_number=trn_no,
                                           trans_date=current_date, total=openingbalance, balance=openingbalance, party=part)

                if request.user.is_company:
                    trans.company = request.user.company
                else:
                    trans.company = request.user.employee.company

                trans.save()

                tr_history = PartyTransactionHistory(party=part, Transactions_party=trans, action="CREATED")
                tr_history.save()

                if request.POST.get('save_and_next'):
                    return redirect('load_party_create')
                elif request.POST.get('save'):
                    return redirect('party_list')

        except IntegrityError:
            # Specific error message for duplicate TRN number
            error_message = 'An error occurred while processing your request. Please try again.'

    return render(request, 'add_parties.html', {'error_message': error_message})









# def addNewParty(request):
#     if request.user.is_company:
#         cmp = request.user.company
#     else:
#         cmp = request.user.employee.company
#         print(cmp)

#     if request.method == 'POST':
#         party_name = request.POST['partyname']
#         trn_no = request.POST['trn_no']
#         contact = request.POST['contact']
#         trn_type = request.POST['trn_type']
#         state = request.POST.get('state')
#         address = request.POST['address']
#         email = request.POST['email']
#         openingbalance = request.POST.get('balance', '')
#         payment = request.POST.get('paymentType', '')
#         current_date = request.POST['currentdate']
#         End_date = request.POST.get('enddate', None)
#         additionalfield1 = request.POST['additionalfield1']
#         additionalfield2 = request.POST['additionalfield2']
#         additionalfield3 = request.POST['additionalfield3']

#         part = Party(party_name=party_name, trn_no=trn_no, contact=contact, trn_type=trn_type, state=state,
#                      address=address, email=email, openingbalance=openingbalance, payment=payment,
#                      current_date=current_date, End_date=End_date, additionalfield1=additionalfield1,
#                      additionalfield2=additionalfield2, additionalfield3=additionalfield3)

#         if request.user.is_company:
#             part.company = request.user.company
#         else:
#             part.company = request.user.employee.company

#         part.save()

#         trans = Transactions_party(user=request.user, trans_type='Opening Balance', trans_number=trn_no,
#                                    trans_date=current_date, total=openingbalance, balance=openingbalance, party=part)

#         if request.user.is_company:
#             trans.company = request.user.company
#         else:
#             trans.company = request.user.employee.company

#         trans.save()

#         tr_history = PartyTransactionHistory(party=part,Transactions_party=trans, action="CREATED")
#         tr_history.save()

#         if request.POST.get('save_and_next'):
#             return redirect('load_party_create')
#         elif request.POST.get('save'):
#             return redirect('party_list')

#     return render(request, 'add_parties.html')









# def addNewParty(request):
#     if request.user.is_company:
#         cmp = request.user.company
#     else:
#         cmp = request.user.employee.company
#         print(cmp)
#     if request.method == 'POST':
#       party_name = request.POST['partyname']
#       trn_no = request.POST['trn_no']
#       contact = request.POST['contact']
#       trn_type = request.POST['trn_type']
#       state = request.POST.get('state')
#       address = request.POST['address']
#       email = request.POST['email']
#       openingbalance = request.POST.get('balance', '')
#       payment = request.POST.get('paymentType', '')
#       current_date = request.POST['currentdate']
#       End_date = request.POST.get('enddate', None)
#       additionalfield1 = request.POST['additionalfield1']
#       additionalfield2 = request.POST['additionalfield2']
#       additionalfield3 = request.POST['additionalfield3']

#       part = Party(party_name=party_name, trn_no=trn_no,contact=contact,trn_type=trn_type, state=state,address=address, email=email, openingbalance=openingbalance,payment=payment,
#                       current_date=current_date,End_date=End_date,additionalfield1=additionalfield1,additionalfield2=additionalfield2,additionalfield3=additionalfield3)
#       part.save()

#       # return JsonResponse({'status':True})
#       trans = Transactions_party(user = request.user,trans_type ='Opening Balance',trans_number=trn_no,trans_date =current_date,total=openingbalance, balance=openingbalance,party=part)
#       tr_history = PartyTransactionHistory(party=part,
#                                               Transactions_party=trans,      
#                                               action="CREATED",)
#       tr_history.save()
#     if request.user.is_company:
#       part.company = request.user.company
#       trans.company = request.user.company

#     else:
#       part.company = request.user.employee.company
#       trans.company = request.user.employee.company
 
#     part.save()
#     trans.save()

#     if request.POST.get('save_and_next'):
#       return redirect('load_party_create')
#     elif request.POST.get('save'):
#       return redirect('party_list')
    



def view_party(request,id):
  if request.user.is_company:
    party = Party.objects.filter(company = request.user.company)
  else:
    party = Party.objects.filter(company = request.user.employee.company)

  fparty = Party.objects.get(id=id)
  ftrans = Transactions_party.objects.filter(party = fparty)
  context = {'party':party, 'usr':request.user, 'fparty':fparty, 'ftrans':ftrans}
  return render(request,'parties_list.html',context)



def edit_party(request,id):
  if request.user.is_company:
    party = Party.objects.filter(company = request.user.company)
  else:
    party = Party.objects.filter(company = request.user.employee.company)

  getparty=Party.objects.get(id=id)
  parties=Party.objects.filter(user=request.user)
  ftrans = Transactions_party.objects.filter(party = getparty)
  return render(request, 'edit_party.html',{'usr':request.user,'party':party,'getparty':getparty,'parties':parties,'ftrans':ftrans})





# from django.shortcuts import render, redirect
# from .models import Party, Transactions_party


from datetime import datetime
from django.shortcuts import get_object_or_404

def edit_saveparty(request, id):
    company = request.user.company if request.user.is_company else request.user.employee.company
    party_qs = Party.objects.filter(company=company)
    getparty = get_object_or_404(Party, id=id, company=company)
    
    trans = None  # Initialize trans here

    if request.method == 'POST':
        # Update party details
        getparty.party_name = request.POST.get('partyname')
        getparty.trn_no = request.POST.get('trn_no')
        getparty.contact = request.POST['contact']
        getparty.trn_type = request.POST['trn_type']
        getparty.state = request.POST['state']
        getparty.address = request.POST['address']
        getparty.email = request.POST['email']
        getparty.openingbalance = request.POST['balance']
        getparty.payment = request.POST.get('paymentType')
        # getparty.current_date = request.POST['currentdate']
        getparty.current_date = datetime.now().strftime('%Y-%m-%d')
        getparty.additionalfield1 = request.POST['additionalfield1']
        getparty.additionalfield2 = request.POST['additionalfield2']
        getparty.additionalfield3 = request.POST['additionalfield3']

        # Save the party changes
        getparty.save()

        # Check if a transaction with the same party_id exists
        existing_transaction = Transactions_party.objects.filter(party_id=id).first()

        # Update or create a new transaction
        if existing_transaction:
            existing_transaction.trans_type = 'Opening Balance'
            existing_transaction.trans_number = getparty.trn_no
            existing_transaction.trans_date = getparty.current_date
            existing_transaction.total = getparty.openingbalance
            existing_transaction.balance = getparty.openingbalance
            existing_transaction.save()

            # Check and update the transaction history action to "UPDATED"
            party_history_entry = PartyTransactionHistory.objects.filter(
                party=getparty, Transactions_party=existing_transaction
            ).first()
            if party_history_entry:
                party_history_entry.action = "UPDATED"
                party_history_entry.save()

        else:
            # Create and save a new transaction
            trans = Transactions_party(
                user=request.user,
                trans_type='Opening Balance',
                trans_number=getparty.trn_no,
                trans_date=getparty.current_date,
                total=getparty.openingbalance,
                balance=getparty.openingbalance,
                party=getparty,
                company=company
            )
            trans.save()

            # Save the transaction history entry with "CREATED" action
            tr_history = PartyTransactionHistory(
                party=getparty,
                Transactions_party=trans,
                action="UPDATED"
            )
            tr_history.save()

        return redirect('view_party', id=getparty.id)

    return render(request, 'edit_party.html', {'getparty': getparty, 'party': party_qs, 'usr': request.user})




# tr_history = PartyTransactionHistory(party=getparty,Transactions_party=trans,action="UPDATED")
#             print(tr_history,'000000000000000000')
#             tr_history.save()


# Remove has_changed function if not used

# from django.utils import timezone

# def edit_saveparty(request, id):
#     if request.user.is_company:
#         party_qs = Party.objects.filter(company=request.user.company)
#     else:
#         party_qs = Party.objects.filter(company=request.user.employee.company)

#     getparty = Party.objects.get(id=id)

#     if request.method == 'POST':
#         # Capture old data before making changes
#         old_data = {
#             'party_name': getparty.party_name,
#             'trn_no': getparty.trn_no,
#             'contact': getparty.contact,
#             'trn_type': getparty.trn_type,
#             'state': getparty.state,
#             'address': getparty.address,
#             'email': getparty.email,
#             'openingbalance': getparty.openingbalance,
#             'payment': getparty.payment,
#             'current_date': getparty.current_date,
#             'additionalfield1': getparty.additionalfield1,
#             'additionalfield2': getparty.additionalfield2,
#             'additionalfield3': getparty.additionalfield3,
#         }

#         getparty.party_name = request.POST.get('partyname', '')
#         # ... (rest of the fields)

#         # Check for changes
#         if old_data != {
#             'party_name': getparty.party_name,
#             'trn_no': getparty.trn_no,
#             'contact': getparty.contact,
#             'trn_type': getparty.trn_type,
#             'state': getparty.state,
#             'address': getparty.address,
#             'email': getparty.email,
#             'openingbalance': getparty.openingbalance,
#             'payment': getparty.payment,
#             'current_date': getparty.current_date,
#             'additionalfield1': getparty.additionalfield1,
#             'additionalfield2': getparty.additionalfield2,
#             'additionalfield3': getparty.additionalfield3,
#         }:
#             # Changes detected, update history

#             # Save the party changes
#             getparty.save()

#             existing_transaction = Transactions_party.objects.filter(party=getparty).first()

#             if existing_transaction:
#                 existing_transaction.trans_type = 'Opening Balance'
#                 existing_transaction.trans_number = getparty.trn_no
#                 existing_transaction.trans_date = getparty.current_date
#                 existing_transaction.total = getparty.openingbalance
#                 existing_transaction.balance = getparty.openingbalance
#                 existing_transaction.save()

#             else:
#                 trans = Transactions_party(
#                     user=request.user,
#                     trans_type='Opening Balance',
#                     trans_number=getparty.trn_no,
#                     trans_date=getparty.current_date,
#                     total=getparty.openingbalance,
#                     balance=getparty.openingbalance,
#                     party=getparty
#                 )

#                 if request.user.is_company:
#                     trans.company = request.user.company
#                 else:
#                     trans.company = request.user.employee.company

#                 trans.save()

#                 # Now that trans is created, create history entry
#                 history_entry = PartyTransactionHistory(
#                     party=getparty,
#                     Transactions_party=trans,
#                     action="UPDATED",
#                     # Update with the current timestamp
#                 )
#                 history_entry.save()

#         return redirect('view_party', id=getparty.id)

#     return render(request, 'edit_party.html', {'getparty': getparty, 'party': party_qs, 'usr': request.user})


def history_party(request, id):
    if request.user.is_company:
        party = Party.objects.filter(company=request.user.company)
    else:
        party = Party.objects.filter(company=request.user.employee.company)

    fparty = Party.objects.get(id=id)
    ftrans = Transactions_party.objects.get(party=fparty)
    hst = PartyTransactionHistory.objects.filter(party=id)

    context = {'party': party, 'hst': hst, 'ftrans': ftrans, 'usr': request.user, 'fparty': fparty}
    return render(request, 'partyhistory.html', context)







def deleteparty(request,id):
    if request.user.is_company:
      party = Party.objects.filter(company = request.user.company)
    else:
      party = Party.objects.filter(company = request.user.employee.company)

    party=Party.objects.get(id=id)
    party.delete()
    return redirect('party_list')
    











def shareTransactionpartyToEmail(request,id):
  if request.user.is_company:
      party = Party.objects.filter(company = request.user.company)

  else:
      party = Party.objects.filter(company = request.user.employee.company)
  if request.method == "POST":
        fparty=Party.objects.get(id=id)
        
        ftrans =Transactions_party.objects.filter(party=fparty)
        context = {'party': party, 'usr': request.user, 'fparty': fparty, 'ftrans': ftrans}
       
        
        email_message = request.POST['email_message']
        my_subject = "Transaction REPORT"
        emails_string = request.POST['email_ids']
        emails_list = [email.strip() for email in emails_string.split(',')]
        # recipient_email = request.POST.get('email_ids')
        html_message = render_to_string('transaction_pdf.html',context)#add ur html
        # vyaparapp\templates\index.html
        # vyaparapp\templates\company\gstr3B_pdf.html
        plain_message = strip_tags(html_message)
        pdf_content = BytesIO()
        pisa_document = pisa.CreatePDF(html_message.encode("UTF-8"), pdf_content) 
        pdf_content.seek(0)
        # todo: need to update the from_email
        filename = f'transaction .pdf'
        message = EmailMultiAlternatives(
            subject=my_subject,
            body= f"Hi,\nPlease find the attached Gstr9 Report -  \n{email_message}\n--\nRegards,\n",
            from_email='altostechnologies6@gmail.com',
            to= emails_list ,  # Use the recipient_email variable here
            )
        message.attach(filename, pdf_content.read(), 'application/pdf')
        
        try:
            message.send()
            return HttpResponse('<script>alert("Report has been shared via successfully..!");window.location="/party_list"</script>')
        except Exception as e:
            # Handle the exception, log the error, or provide an error message
            return HttpResponse('<script>alert("Failed to send email!");window.location="/party_list"</script>')

  return HttpResponse('<script>alert("Invalid Request!");window.location="/party_list"</script>') 








# def itemdetailinvoice(request):
#   if request.user.is_company:
#       company = request.user.company
#       parties = Party.objects.filter(company=company)
#   else:
#       company = request.user.employee.company
#       parties = Party.objects.filter(company=company)
#   itmid = request.GET['id']
#   itm = Item.objects.get(id=itmid)
#   hsn = itm.itm_hsn
#   price = itm.itm_sale_price
#   return JsonResponse({'hsn':hsn, 'price':price}) 

from django.http import JsonResponse

def itemdetailinvoice(request):
    try:
        if request.user.is_company:
            company = request.user.company
            parties = Party.objects.filter(company=company)
        else:
            company = request.user.employee.company
            parties = Party.objects.filter(company=company)

        itmid = request.GET.get('id')  # Using get to avoid KeyError
        itm = Item.objects.get(id=itmid)

        hsn = itm.itm_hsn
        price = itm.itm_sale_price

        return JsonResponse({'hsn': hsn, 'price': price,'parties':parties})
    except Item.DoesNotExist:
        return JsonResponse({'error': 'Item not found'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)







from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.http import HttpResponse
from django.core.exceptions import ObjectDoesNotExist
from .models import Party, Item, SalesInvoice

@login_required
def add_salesinvoice(request):
    try:
        if request.user.is_company:
            company = request.user.company
            parties = Party.objects.filter(company=company)
        else:
            company = request.user.employee.company
            parties = Party.objects.filter(company=company)
            
     
        
        items = Item.objects.filter(company=company)
        
        
        sales_invoices = SalesInvoice.objects.filter(company=company)
        if sales_invoices.exists():
            invoice_count = sales_invoices.last().invoice_no
            next_count = invoice_count + 1
        else:
            next_count = 1


        return render(request, 'add_salesinvoice.html', {'parties': parties, 'usr': request.user, 'count': next_count, 'items': items})

    except ObjectDoesNotExist:
        # Handle the case where the Company or Party object is not found
        return HttpResponse("Error: Company or Party not found.")






def party_details(request, party_name):
    try:
        party = Party.objects.get(party_name=party_name)
        data = {
            'contact': party.contact,
            'address': party.address,
            'openingbalance': party.openingbalance,
            'payment': party.payment,
        }
        return JsonResponse(data)
    except Party.DoesNotExist:
        return JsonResponse({'error': 'Party not found'},status=404)


    

# def itemdata_salesinvoiceedit(request):
#   itmid = request.GET['id']
#   print(itmid)
#   itm = Item.objects.get(id=itmid)
#   print(itm)
#   hsn = itm.itm_hsn
#   # gst = itm.itm_gst
#   # igst = itm.itm_igst
#   price = itm.itm_sale_price
#   qty = itm.itm_at_price
#   return JsonResponse({'hsn':hsn, 'price':price, 'qty':qty})
    








from django.http import Http404

def itemdata_salesinvoiceedit(request):
    try:
        itmid = request.GET['id']
        itm = Item.objects.get(id=itmid)
        hsn = itm.itm_hsn
        # gst = itm.itm_gst
        # igst = itm.itm_igst
        price = itm.itm_sale_price
        qty = itm.itm_at_price
        return JsonResponse({'hsn': hsn, 'price': price, 'qty': qty})
    except Item.DoesNotExist:
        raise Http404("Item not found")
