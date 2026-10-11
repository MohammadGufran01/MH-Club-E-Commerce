import os
import threading

from django.shortcuts import render, redirect, HttpResponse
from django.contrib.auth.models import User
from django.contrib import messages
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.utils.encoding import force_str, force_bytes
from django.core.mail import EmailMessage
from django.conf import settings
from django.views.generic import View
from django.contrib.auth import login, logout, authenticate
from django.db.models import Q

from helper import send_email_async

from .utils import TokenGenerator, generate_token

from django.utils.encoding import DjangoUnicodeDecodeError
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.safestring import mark_safe


# ============================================================
# SIGNUP
# ============================================================

def signup(request):

    if request.method == "POST":

        Name = request.POST.get('name')
        emails = request.POST.get('email')
        password = request.POST.get('pass1')
        confirm_password = request.POST.get('pass2')

        # ==============================
        # CHECK PASSWORD
        # ==============================

        if password != confirm_password:
            messages.warning(request, "Passwords do not match.")
            return render(request, "signup.html")

        # ==============================
        # CHECK EMAIL
        # ==============================

        if User.objects.filter(username=emails).exists():
            messages.info(request, "Email already exists.")
            return render(request, "signup.html")

        # ==============================
        # CREATE USER
        # ==============================

        user = User.objects.create_user(
            username=emails,
            first_name=Name,
            email=emails,
            password=password
        )

        # User remains inactive until email activation
        user.is_active = False
        user.save()

        # ==============================
        # GENERATE ACTIVATION LINK
        # ==============================

        uid = urlsafe_base64_encode(
            force_bytes(user.pk)
        )

        token = generate_token.make_token(user)

        # ======================================================
        # DYNAMIC ACTIVATION LINK
        # ======================================================
        base_url = request.build_absolute_uri('/')[:-1]
        activation_link = f"{base_url}/auth/activate/{uid}/{token}/"

        # ==============================
        # EMAIL CONTENT
        # ==============================

        subject = "Activate Your MH Club Account"

        message = f"""
        <!DOCTYPE html>
        <html>

        <head>
            <meta charset="UTF-8">
            <title>Activate Your MH Club Account</title>
        </head>

        <body style="
            margin:0;
            padding:0;
            background-color:#f4f6f8;
            font-family:Arial, Helvetica, sans-serif;
        ">

            <table
                width="100%"
                cellpadding="0"
                cellspacing="0"
                style="
                    background-color:#f4f6f8;
                    padding:20px 0;
                "
            >

                <tr>
                    <td align="center">

                        <!-- Main Container -->
                        <table
                            width="600"
                            cellpadding="0"
                            cellspacing="0"
                            style="
                                background-color:#ffffff;
                                border-radius:8px;
                                overflow:hidden;
                                box-shadow:0 4px 12px rgba(0,0,0,0.1);
                            "
                        >

                            <!-- Header -->
                            <tr>
                                <td style="
                                    background-color:#111111;
                                    padding:25px;
                                    text-align:center;
                                ">

                                    <h1 style="
                                        color:#ffffff;
                                        margin:0;
                                        font-size:26px;
                                        letter-spacing:1px;
                                    ">
                                        MH Club
                                    </h1>

                                    <p style="
                                        color:#e9ecef;
                                        margin:5px 0 0;
                                        font-size:14px;
                                    ">
                                        Elevate Your Everyday Style & Fashion
                                    </p>

                                </td>
                            </tr>


                            <!-- Body -->
                            <tr>
                                <td style="
                                    padding:30px;
                                    color:#333333;
                                ">

                                    <h2 style="margin-top:0;">
                                        Hi {Name}, 👋
                                    </h2>

                                    <p style="
                                        font-size:15px;
                                        line-height:1.6;
                                    ">
                                        Thank you for creating an account on
                                        <strong>MH Club</strong>.
                                        You are just one step away from accessing
                                        exclusive collections, tracking orders, and enjoying express checkout.
                                    </p>

                                    <p style="
                                        font-size:15px;
                                        line-height:1.6;
                                    ">
                                        Please click the button below to activate
                                        your account:
                                    </p>


                                    <!-- Activation Button -->
                                    <div style="
                                        text-align:center;
                                        margin:30px 0;
                                    ">

                                        <a
                                            href="{activation_link}"
                                            style="
                                                background-color:#111111;
                                                color:#ffffff;
                                                padding:14px 28px;
                                                text-decoration:none;
                                                font-size:16px;
                                                font-weight:bold;
                                                border-radius:6px;
                                                display:inline-block;
                                            "
                                        >
                                            Activate My Account
                                        </a>

                                    </div>


                                    <p style="
                                        font-size:14px;
                                        color:#555;
                                    ">
                                        If the button does not work, copy and paste
                                        the following link into your browser:
                                    </p>

                                    <p style="
                                        font-size:13px;
                                        word-break:break-all;
                                        color:#111111;
                                    ">
                                        {activation_link}
                                    </p>


                                    <p style="
                                        font-size:14px;
                                        line-height:1.6;
                                        margin-top:20px;
                                    ">
                                        If you did not create this account,
                                        you can safely ignore this email.
                                    </p>


                                    <p style="
                                        margin-top:30px;
                                        font-size:14px;
                                    ">
                                        Regards,<br>
                                        <strong>MH Club Team</strong>
                                    </p>

                                </td>
                            </tr>


                            <!-- Footer -->
                            <tr>
                                <td style="
                                    background-color:#f8f9fa;
                                    padding:15px;
                                    text-align:center;
                                    font-size:12px;
                                    color:#6c757d;
                                ">

                                    © 2026 MH Club. All rights reserved.

                                </td>
                            </tr>

                        </table>

                    </td>
                </tr>

            </table>

        </body>
        </html>
        """

        # ==============================
        # CREATE EMAIL
        # ==============================

        email_message = EmailMessage(
            subject=subject,
            body=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[emails],
        )

        # Tell Django this is HTML
        email_message.content_subtype = "html"

        # ==============================
        # SEND EMAIL
        # ==============================

        try:

            # Do NOT use threading while debugging.
            # This allows Django to show the real SMTP error.

            email_message.send(fail_silently=False)

            print("EMAIL SENT SUCCESSFULLY TO:", emails)

        except Exception as e:

            print("EMAIL ERROR:", str(e))

            # Since the user was created but email failed,
            # remove the inactive user so they can try signup again.
            user.delete()

            messages.error(
                request,
                f"Unable to send activation email. Error: {str(e)}"
            )

            return render(request, "signup.html")


        # ==============================
        # SUCCESS MESSAGE
        # ==============================

        messages.success(
            request,
            "Account created successfully! "
            "Please check your email to activate your account."
        )

        return redirect('auth:signup')


    # ==============================
    # GET REQUEST
    # ==============================

    return render(request, "signup.html")


# ============================================================
# ACTIVATE ACCOUNT
# ============================================================

class ActivateAccountView(View):

    def get(self, request, uidb64, token):

        try:

            uid = force_str(
                urlsafe_base64_decode(uidb64)
            )

            user = User.objects.get(pk=uid)

        except Exception as identifier:

            user = None

        if user is not None and generate_token.check_token(user, token):

            if user.is_active:

                messages.info(
                    request,
                    "Your account is already activated."
                )

                return redirect('/auth/login/')

            user.is_active = True
            user.save()

            messages.success(
                request,
                "Account activated successfully! You can now login."
            )

            return redirect('/auth/login/')

        return render(request, 'activatefail.html')


# ============================================================
# LOGIN
# ============================================================

def handlelogin(request):

    if request.user.is_authenticated:
        if request.user.groups.filter(name="DeliveryBoy").exists():
            return redirect("delivery_dashboard")
        if request.user.is_staff or request.user.is_superuser:
            return redirect('/admin/')
        return redirect("/")

    if request.method == "POST":

        identifier = request.POST.get('email', '').strip()
        userpassword = request.POST.get('pass1', '')

        myuser = authenticate(
            request,
            username=identifier,
            password=userpassword
        )

        if myuser is not None:

            if not myuser.is_active:
                messages.warning(
                    request,
                    "Your account is inactive. Please activate your account via email or contact support."
                )
                return redirect('/auth/login/')

            login(request, myuser)

            messages.success(
                request,
                "Login Success!"
            )

            if myuser.groups.filter(name="DeliveryBoy").exists():
                return redirect("delivery_dashboard")

            if myuser.is_staff or myuser.is_superuser:
                return redirect('/admin/')

            return redirect("/")

        # Check if credentials match an existing account that is not yet activated
        try:
            inactive_user = User.objects.filter(
                Q(username__iexact=identifier) | Q(email__iexact=identifier)
            ).first()
            if inactive_user and inactive_user.check_password(userpassword) and not inactive_user.is_active:
                messages.warning(
                    request,
                    "Your account has not been activated yet. Please check your email for the activation link."
                )
                return redirect('/auth/login/')
        except Exception:
            pass

        messages.error(
            request,
            'Invalid Credentials'
        )

        return redirect('/auth/login/')

    return render(request, 'login.html')


# ============================================================
# LOGOUT
# ============================================================

def handlelogout(request):

    logout(request)

    messages.info(
        request,
        "Logout Success!"
    )

    return redirect('/auth/login/')


# ============================================================
# REQUEST PASSWORD RESET EMAIL
# ============================================================

class RequestResetEmailView(View):

    def get(self, request):

        return render(
            request,
            'request-reset-email.html'
        )


    def post(self, request):

        email = request.POST['email']

        user = User.objects.filter(email=email)

        if user.exists():

            user = user.first()

            # ==============================
            # GENERATE UID
            # ==============================

            uid = urlsafe_base64_encode(
                force_bytes(user.pk)
            )

            # ==============================
            # GENERATE RESET TOKEN
            # ==============================

            token = PasswordResetTokenGenerator().make_token(user)

            # ======================================================
            # DYNAMIC PASSWORD RESET LINK
            # ======================================================
            base_url = request.build_absolute_uri('/')[:-1]
            reset_link = f"{base_url}/auth/set-new-password/{uid}/{token}/"

            # ==============================
            # EMAIL CONTENT
            # ==============================

            message = f"""
            <!DOCTYPE html>
            <html>

            <head>
                <meta charset="UTF-8">
                <title>Reset Your MH Club Password</title>
            </head>

            <body style="
                margin:0;
                padding:0;
                background-color:#f4f6f8;
                font-family:Arial, Helvetica, sans-serif;
            ">

            <table
                width="100%"
                cellpadding="0"
                cellspacing="0"
                style="padding:20px 0;"
            >

            <tr>
                <td align="center">

                <!-- Main Card -->
                <table
                    width="600"
                    cellpadding="0"
                    cellspacing="0"
                    style="
                        background:#ffffff;
                        border-radius:8px;
                        box-shadow:0 4px 12px rgba(0,0,0,0.1);
                        overflow:hidden;
                    "
                >

                    <!-- Header -->
                    <tr>
                    <td style="
                        background:#111111;
                        padding:25px;
                        text-align:center;
                    ">

                        <h1 style="
                            margin:0;
                            color:#ffffff;
                            letter-spacing:1px;
                        ">
                            MH Club
                        </h1>

                        <p style="
                            margin:5px 0 0;
                            color:#e9ecef;
                        ">
                            Password Reset Request
                        </p>

                    </td>
                    </tr>


                    <!-- Body -->
                    <tr>
                    <td style="
                        padding:30px;
                        color:#333333;
                    ">

                        <h2 style="margin-top:0;">
                            Hi {user.first_name}, 👋
                        </h2>

                        <p style="
                            font-size:15px;
                            line-height:1.6;
                        ">
                            We received a request to reset your
                            <strong>MH Club</strong> account password.
                        </p>

                        <p style="font-size:15px;">
                            Click the button below to set a new password:
                        </p>


                        <!-- Button -->
                        <div style="
                            text-align:center;
                            margin:30px 0;
                        ">

                            <a
                                href="{reset_link}"
                                style="
                                    background:#111111;
                                    color:#ffffff;
                                    padding:14px 28px;
                                    text-decoration:none;
                                    font-size:16px;
                                    font-weight:bold;
                                    border-radius:6px;
                                    display:inline-block;
                                "
                            >
                                Reset Password
                            </a>

                        </div>


                        <p style="
                            font-size:14px;
                            color:#555;
                        ">
                            If the button doesn’t work, copy and paste
                            this link into your browser:
                        </p>

                        <p style="
                            font-size:13px;
                            word-break:break-all;
                            color:#111111;
                        ">
                            {reset_link}
                        </p>


                        <p style="
                            font-size:14px;
                            margin-top:20px;
                        ">
                            If you did not request a password reset,
                            you can safely ignore this email.
                        </p>


                        <p style="margin-top:30px;">
                            Regards,<br>
                            <strong>MH Club Team</strong>
                        </p>

                    </td>
                    </tr>


                    <!-- Footer -->
                    <tr>
                    <td style="
                        background:#f8f9fa;
                        padding:12px;
                        text-align:center;
                        font-size:12px;
                        color:#6c757d;
                    ">

                        © 2026 MH Club. All rights reserved.

                    </td>
                    </tr>

                </table>

                </td>
            </tr>

            </table>

            </body>
            </html>
            """


            # ==============================
            # CREATE RESET EMAIL
            # ==============================

            email_message = EmailMessage(
                subject="Reset Your BuyZone Password",
                body=message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=[email],
            )

            email_message.content_subtype = "html"


            # ==============================
            # SEND RESET EMAIL
            # ==============================

            threading.Thread(
                target=send_email_async,
                args=(email_message,)
            ).start()


            messages.success(
                request,
                "We have sent you an email with instructions "
                "to reset your password."
            )

            return redirect(
                'auth:request-reset-email'
            )


        messages.error(
            request,
            "No account found with this email."
        )

        return redirect(
            'auth:request-reset-email'
        )


# ============================================================
# SET NEW PASSWORD
# ============================================================

class SetNewPasswordView(View):

    def get(self, request, uidb64, token):

        context = {
            'uidb64': uidb64,
            'token': token
        }

        try:

            user_id = force_str(
                urlsafe_base64_decode(uidb64)
            )

            user = User.objects.get(pk=user_id)

            if not PasswordResetTokenGenerator().check_token(
                user,
                token
            ):

                messages.error(
                    request,
                    "Password reset link is invalid or expired."
                )

                return redirect(
                    'auth:request-reset-email'
                )

            messages.success(
                request,
                "User verified. You can now set a new password."
            )

        except (
            TypeError,
            ValueError,
            OverflowError,
            User.DoesNotExist
        ):

            messages.error(
                request,
                "Invalid password reset link."
            )

            return redirect(
                'auth:request-reset-email'
            )

        return render(
            request,
            'set-new-password.html',
            context
        )


    def post(self, request, uidb64, token):

        password = request.POST.get('pass1')
        confirm_password = request.POST.get('pass2')

        context = {
            'uidb64': uidb64,
            'token': token
        }

        # ==============================
        # CHECK EMPTY PASSWORD
        # ==============================

        if not password or not confirm_password:

            messages.warning(
                request,
                "Password fields cannot be empty."
            )

            return render(
                request,
                'set-new-password.html',
                context
            )


        # ==============================
        # CHECK PASSWORD MATCH
        # ==============================

        if password != confirm_password:

            messages.warning(
                request,
                "Passwords do not match."
            )

            return render(
                request,
                'set-new-password.html',
                context
            )


        # ==============================
        # FIND USER
        # ==============================

        try:

            user_id = force_str(
                urlsafe_base64_decode(uidb64)
            )

            user = User.objects.get(pk=user_id)


            # ==============================
            # CHECK RESET TOKEN
            # ==============================

            if not PasswordResetTokenGenerator().check_token(
                user,
                token
            ):

                messages.error(
                    request,
                    "Password reset link has expired."
                )

                return redirect(
                    'auth:request-reset-email'
                )


            # ==============================
            # SET NEW PASSWORD
            # ==============================

            user.set_password(password)
            user.save()


            messages.success(
                request,
                "Password reset successful. "
                "Please login with your new password."
            )

            return redirect(
                'auth:handlelogin'
            )


        except (
            TypeError,
            ValueError,
            OverflowError,
            User.DoesNotExist
        ):

            messages.error(
                request,
                "Something went wrong. Please try again."
            )

            return redirect(
                'auth:request-reset-email'
            )

